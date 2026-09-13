import os
import json
from typing import Dict, Any, Optional
from app.services.analytics_service import AnalyticsService
from app.services.forecast_service import ForecastService


class AIService:
    @staticmethod
    def get_api_key() -> Optional[str]:
        """
        Retrieve Gemini API key from environment.
        """
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or not api_key.strip() or api_key == 'your_api_key_here':
            return None
        return api_key.strip()

    @classmethod
    def generate_business_insights(cls) -> Dict[str, Any]:
        """
        Gathers analytics and forecasting context, prompts Gemini AI, and returns structured insights.
        """
        # 1. Gather all calculated business metrics
        summary = AnalyticsService.get_summary()

        if summary['invoice_count'] == 0:
            return {
                'status': 'no_data',
                'message': 'No invoices found in database. Create invoices first to generate AI business insights.',
                'insights': None
            }

        monthly_sales = AnalyticsService.get_monthly_sales()
        monthly_profit = AnalyticsService.get_monthly_profit()
        top_products = AnalyticsService.get_top_products(limit=5)
        profitable_products = AnalyticsService.get_most_profitable_products(limit=5)
        gst_summary = AnalyticsService.get_gst_summary()
        forecast = ForecastService.forecast_sales(months_ahead=3)

        context_data = {
            'kpi_summary': summary,
            'monthly_sales_trend': monthly_sales,
            'monthly_profit_trend': monthly_profit,
            'top_revenue_products': top_products,
            'most_profitable_products': profitable_products,
            'tax_gst_breakdown': gst_summary,
            'sales_forecast': forecast
        }

        # 2. Check for Gemini API key
        api_key = cls.get_api_key()
        if not api_key:
            return {
                'status': 'warning',
                'message': 'GEMINI_API_KEY not configured. Returning rule-based preliminary insight summary.',
                'context_metrics': context_data,
                'insights': cls._generate_rule_based_fallback(summary, top_products, forecast)
            }

        # 3. Build Prompt for Gemini
        prompt = cls._build_insight_prompt(context_data)
        model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')

        try:
            # Try official google-genai client first
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                raw_text = response.text.strip()
            except ImportError:
                import google.generativeai as legacy_genai
                legacy_genai.configure(api_key=api_key)
                model = legacy_genai.GenerativeModel(
                    model_name=model_name,
                    generation_config={"response_mime_type": "application/json"}
                )
                response = model.generate_content(prompt)
                raw_text = response.text.strip()

            clean_text = raw_text.strip()
            if clean_text.startswith("```"):
                lines = clean_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                clean_text = "\n".join(lines).strip()

            parsed_insights = json.loads(clean_text)

            return {
                'status': 'success',
                'model': model_name,
                'insights': parsed_insights,
                'context_metrics': context_data
            }

        except Exception as e:
            # Graceful fallback to rule-based insights if Gemini call fails
            return {
                'status': 'fallback_error',
                'message': f"Gemini API invocation failed ({str(e)}). Fallback insights provided.",
                'context_metrics': context_data,
                'insights': cls._generate_rule_based_fallback(summary, top_products, forecast)
            }

    @staticmethod
    def _build_insight_prompt(context_data: Dict[str, Any]) -> str:
        return f"""
You are an expert Chief Financial Officer (CFO) and Senior Business Analytics Consultant.
Analyze the following verified business data and produce actionable, strategic insights.

IMPORTANT RULES:
1. Do NOT invent or recalculate any financial numbers. Rely strictly on the numbers provided in the data.
2. Return your response ONLY as a valid JSON object matching the exact schema specified below.
3. Keep observations sharp, concise, and business-focused.

BUSINESS DATA:
{json.dumps(context_data, indent=2)}

REQUIRED JSON RESPONSE SCHEMA:
{{
  "executive_summary": "Short 2-3 sentence overview of company financial health.",
  "key_observations": [
    "Observation 1 regarding revenue or profit margin",
    "Observation 2 regarding product or sales trends"
  ],
  "business_risks": [
    "Identified risk 1 (e.g., customer/product concentration, margin compression)",
    "Identified risk 2"
  ],
  "growth_opportunities": [
    "Opportunity 1 (e.g., upsell high-margin items, expand product lines)",
    "Opportunity 2"
  ],
  "actionable_recommendations": [
    "Immediate action step 1",
    "Immediate action step 2",
    "Immediate action step 3"
  ]
}}
"""

    @staticmethod
    def _generate_rule_based_fallback(summary: Dict[str, Any], top_products: list, forecast: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rule-based fallback summary if Gemini API is unreachable or key is unset.
        """
        margin = summary.get('profit_margin', 0.0)
        revenue = summary.get('total_revenue', 0.0)
        top_prod_name = top_products[0]['product_name'] if top_products else "N/A"

        health = "healthy" if margin >= 20 else ("moderate" if margin >= 10 else "tight")

        return {
            'executive_summary': f"Total revenue stands at ${revenue:,.2f} with a {health} overall profit margin of {margin}%.",
            'key_observations': [
                f"Generated ${revenue:,.2f} across {summary.get('invoice_count', 0)} invoices with an average order value of ${summary.get('average_invoice_value', 0):,.2f}.",
                f"Top revenue driver is '{top_prod_name}' with strong contribution." if top_products else "Invoice data is currently limited."
            ],
            'business_risks': [
                "Monitor purchase cost fluctuations to maintain healthy gross margins.",
                "Ensure revenue is diversified across multiple customers and products."
            ],
            'growth_opportunities': [
                f"Promote high-margin products to boost overall margin above {margin}%.",
                "Explore volume discounts on fast-moving line items."
            ],
            'actionable_recommendations': [
                "Review supplier pricing for key product lines.",
                "Implement proactive customer follow-ups on regular invoice cycles.",
                "Track monthly sales velocity against forecasting targets."
            ]
        }
