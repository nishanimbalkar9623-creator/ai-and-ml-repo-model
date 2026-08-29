import json


class TestForecastingAPI:
    def test_forecast_empty_data(self, client):
        response = client.get('/api/forecast/sales')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'insufficient_data'
        assert 'at least 3 months' in data['message'].lower()
        assert data['forecast'] == []

    def test_forecast_two_months_insufficient(self, client):
        for month in ['2026-01-15', '2026-02-15']:
            payload = {
                'customer_name': 'Test Client',
                'invoice_date': month,
                'gst_percentage': 18.0,
                'items': [{'product_name': 'Item A', 'quantity': 1, 'purchase_price': 100.0, 'selling_price': 200.0}]
            }
            client.post('/api/invoices', data=json.dumps(payload), content_type='application/json')

        response = client.get('/api/forecast/sales')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'insufficient_data'
        assert data['historical_months_count'] == 2

    def test_forecast_with_sufficient_data(self, client):
        # Insert 4 consecutive months of sales data
        monthly_sales = [
            ('2026-01-10', 1000.0),
            ('2026-02-10', 1500.0),
            ('2026-03-10', 2000.0),
            ('2026-04-10', 2500.0)
        ]

        for date_str, price in monthly_sales:
            payload = {
                'customer_name': 'Growth Client',
                'invoice_date': date_str,
                'gst_percentage': 0.0,
                'items': [{'product_name': 'SaaS Plan', 'quantity': 1, 'purchase_price': 500.0, 'selling_price': price}]
            }
            client.post('/api/invoices', data=json.dumps(payload), content_type='application/json')

        response = client.get('/api/forecast/sales?months=3')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['trend_direction'] == 'upward'
        assert data['forecast_periods_ahead'] == 3
        assert len(data['forecast']) == 3

        # First forecast period should be 2026-05
        f1 = data['forecast'][0]
        assert f1['period'] == '2026-05'
        assert f1['predicted_sales'] >= 2500.0
        assert f1['lower_bound'] <= f1['predicted_sales']
        assert f1['upper_bound'] >= f1['predicted_sales']
        assert 'disclaimer' in data
