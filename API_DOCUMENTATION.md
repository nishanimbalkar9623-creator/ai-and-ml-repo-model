# AI Invoice, Business Analytics & Sales Forecasting API Documentation

Comprehensive REST API documentation for the Flask backend.

---

## Base URL
```text
http://localhost:5000
```

---

## 1. System Endpoints

### 1.1 Health Check
* **Method**: `GET`
* **URL**: `/health`
* **Description**: Verifies backend server and database availability.
* **Response `200 OK`**:
```json
{
  "database": "connected",
  "status": "healthy"
}
```

### 1.2 Groq AI Health & Model Registry
* **Method**: `GET`
* **URL**: `/api/health`
* **Description**: Returns the online status, AI provider, and list of supported Groq models.
* **Response `200 OK`**:
```json
{
  "status": "online",
  "provider": "Groq",
  "models": [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama-3.2-11b-vision-preview",
    "llama-3.2-3b-preview",
    "llama-3.2-1b-preview",
    "mixtral-8x7b-32768",
    "gemma2-9b-it"
  ]
}
```

---

## 2. Invoice Management (`/api/invoices`)

### 2.1 Create Invoice
* **Method**: `POST`
* **URL**: `/api/invoices`
* **Description**: Creates a new customer invoice with line items. Calculates subtotal, item cost, item profit, GST amount, total amount, total cost, net profit, and profit margin server-side.
* **Request JSON**:
```json
{
  "customer_name": "Acme Global Corp",
  "invoice_date": "2026-03-15",
  "gst_percentage": 18.0,
  "items": [
    {
      "product_name": "Cloud Infrastructure",
      "quantity": 2,
      "purchase_price": 50.0,
      "selling_price": 120.0
    },
    {
      "product_name": "Domain SSL",
      "quantity": 1,
      "purchase_price": 10.0,
      "selling_price": 30.0
    }
  ]
}
```
* **Response `201 Created`**:
```json
{
  "message": "Invoice created successfully",
  "invoice": {
    "id": 1,
    "customer_name": "Acme Global Corp",
    "invoice_date": "2026-03-15",
    "subtotal": 270.0,
    "gst_percentage": 18.0,
    "gst_amount": 48.6,
    "total_amount": 318.6,
    "total_cost": 110.0,
    "profit": 160.0,
    "profit_margin": 59.26,
    "created_at": "2026-03-15T12:00:00",
    "items": [
      {
        "id": 1,
        "invoice_id": 1,
        "product_name": "Cloud Infrastructure",
        "quantity": 2,
        "purchase_price": 50.0,
        "selling_price": 120.0,
        "item_subtotal": 240.0,
        "item_cost": 100.0,
        "item_profit": 140.0,
        "item_profit_margin": 58.33
      },
      {
        "id": 2,
        "invoice_id": 1,
        "product_name": "Domain SSL",
        "quantity": 1,
        "purchase_price": 10.0,
        "selling_price": 30.0,
        "item_subtotal": 30.0,
        "item_cost": 10.0,
        "item_profit": 20.0,
        "item_profit_margin": 66.67
      }
    ]
  }
}
```
* **Possible Errors**:
  - `400 Bad Request`: Missing customer name, invalid date format, negative price/quantity, GST not between 0-100%, or empty items list.

---

### 2.2 Get All Invoices
* **Method**: `GET`
* **URL**: `/api/invoices`
* **Query Parameters (Optional)**:
  - `start_date`: Filter invoices on or after `YYYY-MM-DD`
  - `end_date`: Filter invoices on or before `YYYY-MM-DD`
  - `customer_name`: Search customer name substring (case-insensitive)
* **Response `200 OK`**:
```json
{
  "count": 1,
  "invoices": [
    {
      "id": 1,
      "customer_name": "Acme Global Corp",
      "invoice_date": "2026-03-15",
      "subtotal": 270.0,
      "gst_percentage": 18.0,
      "gst_amount": 48.6,
      "total_amount": 318.6,
      "total_cost": 110.0,
      "profit": 160.0,
      "profit_margin": 59.26,
      "created_at": "2026-03-15T12:00:00",
      "items": [...]
    }
  ]
}
```

---

### 2.3 Get Single Invoice
* **Method**: `GET`
* **URL**: `/api/invoices/<id>`
* **Response `200 OK`**:
```json
{
  "invoice": {
    "id": 1,
    "customer_name": "Acme Global Corp",
    "invoice_date": "2026-03-15",
    "subtotal": 270.0,
    "gst_percentage": 18.0,
    "gst_amount": 48.6,
    "total_amount": 318.6,
    "total_cost": 110.0,
    "profit": 160.0,
    "profit_margin": 59.26,
    "items": [...]
  }
}
```
* **Possible Errors**:
  - `404 Not Found`: Invoice ID does not exist.

---

### 2.4 Update Invoice
* **Method**: `PUT`
* **URL**: `/api/invoices/<id>`
* **Request JSON**: Full invoice payload with updated fields/items.
* **Response `200 OK`**: Updated invoice object with recalculated financial totals.
* **Possible Errors**:
  - `400 Bad Request`: Invalid payload or negative values.
  - `404 Not Found`: Invoice ID does not exist.

---

### 2.5 Delete Invoice
* **Method**: `DELETE`
* **URL**: `/api/invoices/<id>`
* **Response `200 OK`**:
```json
{
  "message": "Invoice 1 deleted successfully"
}
```
* **Possible Errors**:
  - `404 Not Found`: Invoice ID does not exist.

---

## 3. Analytics (`/api/analytics`)

### 3.1 KPI Summary
* **Method**: `GET`
* **URL**: `/api/analytics/summary`
* **Description**: Returns consolidated business KPIs.
* **Response `200 OK`**:
```json
{
  "average_invoice_value": 318.6,
  "invoice_count": 1,
  "profit_margin": 59.26,
  "total_cost": 110.0,
  "total_gst": 48.6,
  "total_profit": 160.0,
  "total_revenue": 318.6
}
```

---

### 3.2 Monthly Sales Trend
* **Method**: `GET`
* **URL**: `/api/analytics/monthly-sales`
* **Description**: Returns monthly sales totals, invoice volume, and Month-over-Month (MoM) growth rates.
* **Response `200 OK`**:
```json
{
  "count": 2,
  "monthly_sales": [
    {
      "growth_rate_pct": null,
      "invoice_count": 1,
      "month": 1,
      "period": "2026-01",
      "total_sales": 12500.0,
      "year": 2026
    },
    {
      "growth_rate_pct": 14.4,
      "invoice_count": 2,
      "month": 2,
      "period": "2026-02",
      "total_sales": 14300.0,
      "year": 2026
    }
  ]
}
```

---

### 3.3 Monthly Profit Trend
* **Method**: `GET`
* **URL**: `/api/analytics/monthly-profit`
* **Description**: Returns monthly profit totals, profit margins, and profit growth rates.
* **Response `200 OK`**:
```json
{
  "count": 2,
  "monthly_profit": [
    {
      "month": 1,
      "period": "2026-01",
      "profit_growth_pct": null,
      "profit_margin": 45.2,
      "total_profit": 5650.0,
      "year": 2026
    }
  ]
}
```

---

### 3.4 Top Products
* **Method**: `GET`
* **URL**: `/api/analytics/top-products?limit=10`
* **Response `200 OK`**:
```json
{
  "count": 2,
  "top_products": [
    {
      "product_name": "Cloud Infrastructure",
      "profit_margin": 58.33,
      "total_profit": 140.0,
      "total_quantity": 2,
      "total_revenue": 240.0
    }
  ]
}
```

---

### 3.5 Most Profitable Products
* **Method**: `GET`
* **URL**: `/api/analytics/most-profitable-products?limit=10`
* **Response `200 OK`**: List of products ranked by total profit generated.

---

### 3.6 GST Tax Slabs Summary
* **Method**: `GET`
* **URL**: `/api/analytics/gst-summary`
* **Description**: Breakdown of sales and tax collected grouped by GST percentage.
* **Response `200 OK`**:
```json
{
  "count": 1,
  "gst_summary": [
    {
      "gst_percentage": 18.0,
      "invoice_count": 1,
      "total_amount_with_tax": 318.6,
      "total_gst": 48.6,
      "total_taxable_subtotal": 270.0
    }
  ]
}
```

---

## 4. Sales Forecasting (`/api/forecast`)

### 4.1 Predict Future Sales
* **Method**: `GET`
* **URL**: `/api/forecast/sales?months=3`
* **Query Parameters**:
  - `months`: Number of future months to forecast (Default: 3, Min: 1, Max: 24).
* **Response `200 OK` (Sufficient Data $\ge 3$ months)**:
```json
{
  "disclaimer": "Forecasting results are statistical estimations based on historical sales trajectories. Predictions do not account for unforeseen market events or external macroeconomic factors.",
  "forecast": [
    {
      "lower_bound": 14200.0,
      "month": 4,
      "period": "2026-04",
      "predicted_sales": 15600.0,
      "upper_bound": 17000.0,
      "year": 2026
    }
  ],
  "forecast_periods_ahead": 3,
  "historical_data": [...],
  "historical_periods_used": 3,
  "model_type": "Linear Trend Regression (Scikit-Learn)",
  "slope_per_month": 1250.0,
  "status": "success",
  "trend_direction": "upward"
}
```
* **Response `200 OK` (Insufficient Data $< 3$ months)**:
```json
{
  "forecast": [],
  "historical_data": [...],
  "historical_months_count": 1,
  "message": "Insufficient historical data for forecasting. Found 1 month(s), but at least 3 months of historical sales data are required to generate reliable predictions.",
  "required_months_count": 3,
  "status": "insufficient_data"
}
```

---

## 5. Gemini AI Business Insights (`/api/ai`)

### 5.1 Generate Business Insights
* **Method**: `POST` or `GET`
* **URL**: `/api/ai/insights`
* **Description**: Feeds calculated KPI summaries, monthly trends, top products, and forecasts to Google Gemini AI to synthesize executive-level insights without financial number hallucinations.
* **Response `200 OK`**:
```json
{
  "context_metrics": {
    "kpi_summary": {...},
    "monthly_profit_trend": [...],
    "monthly_sales_trend": [...],
    "sales_forecast": {...},
    "top_revenue_products": [...]
  },
  "insights": {
    "actionable_recommendations": [
      "Renegotiate wholesale vendor pricing on Cloud Infrastructure to expand gross margins.",
      "Bundle high-margin Domain SSL certificates with Enterprise software packages.",
      "Schedule quarterly customer retention check-ins to prevent churn."
    ],
    "business_risks": [
      "Top product accounts for over 65% of monthly revenue, exposing the business to product concentration risk."
    ],
    "executive_summary": "Company demonstrates solid financial vitality with an operating margin of 59.26% across recent invoices.",
    "growth_opportunities": [
      "Upsell additional support packages to existing cloud infrastructure clients."
    ],
    "key_observations": [
      "Revenue expanded steadily with an average invoice transaction size of $318.60."
    ]
  },
  "model": "gemini-1.5-flash",
  "status": "success"
}
```
* **Fallback Behavior**:
  - If no invoices exist: returns status `no_data`.
  - If `GEMINI_API_KEY` is not set or network fails: returns status `warning` or `fallback_error` with heuristic fallback insights instead of throwing a server 500 error.
