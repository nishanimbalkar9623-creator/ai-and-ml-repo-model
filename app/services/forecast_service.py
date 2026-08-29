import numpy as np
from datetime import datetime
from typing import Dict, Any, List
from sklearn.linear_model import LinearRegression
from app.services.analytics_service import AnalyticsService


class ForecastService:
    @staticmethod
    def forecast_sales(months_ahead: int = 3) -> Dict[str, Any]:
        """
        Generates statistical sales projections using historical monthly data and Scikit-Learn.
        """
        # Validate months_ahead parameter
        if not isinstance(months_ahead, int) or months_ahead < 1:
            months_ahead = 3
        if months_ahead > 24:
            months_ahead = 24

        monthly_data = AnalyticsService.get_monthly_sales()

        # Check for sufficient historical data (at least 3 data points required)
        if len(monthly_data) < 3:
            return {
                'status': 'insufficient_data',
                'message': (
                    f"Insufficient historical data for forecasting. Found {len(monthly_data)} month(s), "
                    "but at least 3 months of historical sales data are required to generate reliable predictions."
                ),
                'historical_months_count': len(monthly_data),
                'required_months_count': 3,
                'historical_data': monthly_data,
                'forecast': []
            }

        # Prepare training dataset
        # X = sequential integer indices (0, 1, 2, ...)
        # y = total sales for each month
        X = np.array(range(len(monthly_data))).reshape(-1, 1)
        y = np.array([m['total_sales'] for m in monthly_data])

        # Train model
        model = LinearRegression()
        model.fit(X, y)

        # Calculate residual standard error for confidence intervals
        predictions_train = model.predict(X)
        residuals = y - predictions_train
        std_error = float(np.std(residuals)) if len(residuals) > 1 else 0.0

        # Determine last recorded year and month
        last_item = monthly_data[-1]
        last_year = last_item['year']
        last_month = last_item['month']

        forecast_results: List[Dict[str, Any]] = []

        for step in range(1, months_ahead + 1):
            future_idx = np.array([[len(monthly_data) - 1 + step]])
            predicted_sales = float(model.predict(future_idx)[0])
            predicted_sales = max(0.0, predicted_sales)  # Sales cannot be negative

            # Calculate calendar month for future step
            total_months = last_month + step
            future_year = last_year + (total_months - 1) // 12
            future_month = ((total_months - 1) % 12) + 1
            period_str = f"{future_year:04d}-{future_month:02d}"

            # 90% confidence margin estimate (~1.645 * std_error)
            margin = 1.645 * std_error
            lower_bound = max(0.0, round(predicted_sales - margin, 2))
            upper_bound = round(predicted_sales + margin, 2)

            forecast_results.append({
                'period': period_str,
                'year': future_year,
                'month': future_month,
                'predicted_sales': round(predicted_sales, 2),
                'lower_bound': lower_bound,
                'upper_bound': upper_bound
            })

        # Calculate trend direction
        slope = float(model.coef_[0])
        trend_direction = "upward" if slope > 10 else ("downward" if slope < -10 else "stable")

        return {
            'status': 'success',
            'model_type': 'Linear Trend Regression (Scikit-Learn)',
            'trend_direction': trend_direction,
            'slope_per_month': round(slope, 2),
            'historical_periods_used': len(monthly_data),
            'forecast_periods_ahead': months_ahead,
            'historical_data': monthly_data,
            'forecast': forecast_results,
            'disclaimer': (
                "Forecasting results are statistical estimations based on historical sales trajectories. "
                "Predictions do not account for unforeseen market events or external macroeconomic factors."
            )
        }
