import json


class TestAnalyticsAPI:
    def test_empty_analytics_summary(self, client):
        response = client.get('/api/analytics/summary')
        assert response.status_code == 200
        data = response.get_json()
        assert data['total_revenue'] == 0.0
        assert data['total_cost'] == 0.0
        assert data['total_profit'] == 0.0
        assert data['invoice_count'] == 0
        assert data['profit_margin'] == 0.0

    def test_analytics_with_data(self, client):
        # Insert invoice 1: Jan 2026
        inv1 = {
            'customer_name': 'Alpha Corp',
            'invoice_date': '2026-01-10',
            'gst_percentage': 18.0,
            'items': [
                {'product_name': 'Software License', 'quantity': 10, 'purchase_price': 100.0, 'selling_price': 200.0},
                {'product_name': 'Support Pack', 'quantity': 5, 'purchase_price': 20.0, 'selling_price': 50.0}
            ]
        }
        client.post('/api/invoices', data=json.dumps(inv1), content_type='application/json')

        # Insert invoice 2: Feb 2026
        inv2 = {
            'customer_name': 'Beta Corp',
            'invoice_date': '2026-02-15',
            'gst_percentage': 12.0,
            'items': [
                {'product_name': 'Software License', 'quantity': 5, 'purchase_price': 100.0, 'selling_price': 200.0},
                {'product_name': 'Hardware Node', 'quantity': 2, 'purchase_price': 400.0, 'selling_price': 600.0}
            ]
        }
        client.post('/api/invoices', data=json.dumps(inv2), content_type='application/json')

        # Summary check
        res_summary = client.get('/api/analytics/summary')
        assert res_summary.status_code == 200
        summary = res_summary.get_json()
        assert summary['invoice_count'] == 2
        assert summary['total_revenue'] > 0
        assert summary['total_profit'] > 0
        assert summary['profit_margin'] > 0

        # Monthly sales check
        res_sales = client.get('/api/analytics/monthly-sales')
        assert res_sales.status_code == 200
        sales_data = res_sales.get_json()['monthly_sales']
        assert len(sales_data) == 2
        assert sales_data[0]['period'] == '2026-01'
        assert sales_data[1]['period'] == '2026-02'
        assert sales_data[1]['growth_rate_pct'] is not None

        # Monthly profit check
        res_profit = client.get('/api/analytics/monthly-profit')
        assert res_profit.status_code == 200
        profit_data = res_profit.get_json()['monthly_profit']
        assert len(profit_data) == 2

        # Top products check
        res_top = client.get('/api/analytics/top-products')
        assert res_top.status_code == 200
        top_products = res_top.get_json()['top_products']
        assert len(top_products) >= 2
        # Software license should be #1 by revenue (10*200 + 5*200 = 3000)
        assert top_products[0]['product_name'] == 'Software License'
        assert top_products[0]['total_quantity'] == 15

        # Most profitable products check
        res_prof_prod = client.get('/api/analytics/most-profitable-products')
        assert res_prof_prod.status_code == 200
        prof_products = res_prof_prod.get_json()['profitable_products']
        assert len(prof_products) >= 2

        # GST summary check
        res_gst = client.get('/api/analytics/gst-summary')
        assert res_gst.status_code == 200
        gst_data = res_gst.get_json()['gst_summary']
        assert len(gst_data) == 2
        percentages = [g['gst_percentage'] for g in gst_data]
        assert 12.0 in percentages
        assert 18.0 in percentages
