import json


class TestEndToEndBusinessLifecycle:
    def test_full_lifecycle(self, client):
        # 1. Health check
        res_health = client.get('/health')
        assert res_health.status_code == 200
        assert res_health.get_json()['status'] == 'healthy'

        # 2. Ingest Multi-Month Invoices
        invoices_to_create = [
            {
                'customer_name': 'Acme Global',
                'invoice_date': '2026-01-15',
                'gst_percentage': 18.0,
                'items': [
                    {'product_name': 'ERP Software', 'quantity': 2, 'purchase_price': 1000.0, 'selling_price': 2500.0},
                    {'product_name': 'Implementation Support', 'quantity': 10, 'purchase_price': 50.0, 'selling_price': 150.0}
                ]
            },
            {
                'customer_name': 'Starlight Media',
                'invoice_date': '2026-02-10',
                'gst_percentage': 18.0,
                'items': [
                    {'product_name': 'Cloud Infrastructure', 'quantity': 5, 'purchase_price': 200.0, 'selling_price': 600.0},
                    {'product_name': 'ERP Software', 'quantity': 1, 'purchase_price': 1000.0, 'selling_price': 2500.0}
                ]
            },
            {
                'customer_name': 'Quantum Labs',
                'invoice_date': '2026-03-05',
                'gst_percentage': 12.0,
                'items': [
                    {'product_name': 'ERP Software', 'quantity': 3, 'purchase_price': 1000.0, 'selling_price': 2500.0},
                    {'product_name': 'Security Audit', 'quantity': 1, 'purchase_price': 500.0, 'selling_price': 1200.0}
                ]
            },
            {
                'customer_name': 'Nexus Ventures',
                'invoice_date': '2026-04-12',
                'gst_percentage': 18.0,
                'items': [
                    {'product_name': 'Cloud Infrastructure', 'quantity': 8, 'purchase_price': 200.0, 'selling_price': 600.0},
                    {'product_name': 'Security Audit', 'quantity': 2, 'purchase_price': 500.0, 'selling_price': 1200.0}
                ]
            }
        ]

        created_ids = []
        for inv_payload in invoices_to_create:
            res = client.post('/api/invoices', data=json.dumps(inv_payload), content_type='application/json')
            assert res.status_code == 201
            inv_data = res.get_json()['invoice']
            created_ids.append(inv_data['id'])
            # Verify calculations
            assert inv_data['subtotal'] > 0
            assert inv_data['total_amount'] == round(inv_data['subtotal'] + inv_data['gst_amount'], 2)
            assert inv_data['profit'] == round(inv_data['subtotal'] - inv_data['total_cost'], 2)

        # 3. Retrieve All Invoices
        res_list = client.get('/api/invoices')
        assert res_list.status_code == 200
        assert res_list.get_json()['count'] == 4

        # 4. Analytics Summary Verification
        res_summary = client.get('/api/analytics/summary')
        assert res_summary.status_code == 200
        summary = res_summary.get_json()
        assert summary['invoice_count'] == 4
        assert summary['total_revenue'] > 0
        assert summary['total_profit'] > 0
        assert summary['profit_margin'] > 0
        assert summary['average_invoice_value'] == round(summary['total_revenue'] / 4, 2)

        # 5. Monthly Sales & Profit Trends
        res_sales = client.get('/api/analytics/monthly-sales')
        assert res_sales.status_code == 200
        monthly_sales = res_sales.get_json()['monthly_sales']
        assert len(monthly_sales) == 4

        res_profit = client.get('/api/analytics/monthly-profit')
        assert res_profit.status_code == 200
        monthly_profit = res_profit.get_json()['monthly_profit']
        assert len(monthly_profit) == 4

        # 6. Top Products & GST Slabs
        res_top = client.get('/api/analytics/top-products')
        assert res_top.status_code == 200
        top_prods = res_top.get_json()['top_products']
        assert top_prods[0]['product_name'] == 'ERP Software'

        res_gst = client.get('/api/analytics/gst-summary')
        assert res_gst.status_code == 200
        gst_slabs = res_gst.get_json()['gst_summary']
        assert len(gst_slabs) == 2  # 12% and 18%

        # 7. Sales Forecasting (4 months of data >= 3 threshold)
        res_forecast = client.get('/api/forecast/sales?months=3')
        assert res_forecast.status_code == 200
        fc_data = res_forecast.get_json()
        assert fc_data['status'] == 'success'
        assert len(fc_data['forecast']) == 3
        assert fc_data['forecast'][0]['period'] == '2026-05'

        # 8. AI Insights
        res_ai = client.post('/api/ai/insights')
        assert res_ai.status_code == 200
        ai_data = res_ai.get_json()
        assert 'insights' in ai_data
        assert 'executive_summary' in ai_data['insights']

        # 9. Invoice Update and Delete
        first_id = created_ids[0]
        res_del = client.delete(f'/api/invoices/{first_id}')
        assert res_del.status_code == 200

        # Verify count decreased
        res_after_del = client.get('/api/invoices')
        assert res_after_del.get_json()['count'] == 3
