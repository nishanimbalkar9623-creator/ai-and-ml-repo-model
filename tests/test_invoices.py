import json
from app.models import Invoice, InvoiceItem


class TestInvoiceAPI:
    def test_create_invoice_success(self, client, sample_invoice_payload):
        response = client.post(
            '/api/invoices',
            data=json.dumps(sample_invoice_payload),
            content_type='application/json'
        )
        assert response.status_code == 201
        data = response.get_json()
        assert 'invoice' in data
        inv = data['invoice']
        assert inv['customer_name'] == 'Acme Corp'
        assert inv['subtotal'] == 225.0  # (2*100) + (1*25) = 225
        assert inv['gst_amount'] == 40.5  # 18% of 225 = 40.5
        assert inv['total_amount'] == 265.5  # 225 + 40.5 = 265.5
        assert inv['total_cost'] == 110.0  # (2*50) + (1*10) = 110
        assert inv['profit'] == 115.0  # 225 - 110 = 115
        assert inv['profit_margin'] == 51.11  # (115/225)*100 = 51.11%
        assert len(inv['items']) == 2

    def test_create_invoice_empty_payload(self, client):
        response = client.post('/api/invoices', data='', content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_create_invoice_validation_failures(self, client):
        invalid_payload = {
            'customer_name': '',
            'invoice_date': '2026-03-15',
            'gst_percentage': -5.0,
            'items': []
        }
        response = client.post(
            '/api/invoices',
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_get_all_invoices(self, client, sample_invoice_payload):
        # Create two invoices
        client.post('/api/invoices', data=json.dumps(sample_invoice_payload), content_type='application/json')
        second_payload = dict(sample_invoice_payload, customer_name='Beta LLC', invoice_date='2026-04-01')
        client.post('/api/invoices', data=json.dumps(second_payload), content_type='application/json')

        # Get all
        response = client.get('/api/invoices')
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 2
        assert len(data['invoices']) == 2

        # Filter by customer name
        res_filter = client.get('/api/invoices?customer_name=Beta')
        assert res_filter.status_code == 200
        assert res_filter.get_json()['count'] == 1

        # Filter by date range
        res_date = client.get('/api/invoices?start_date=2026-04-01')
        assert res_date.status_code == 200
        assert res_date.get_json()['count'] == 1

    def test_get_invoice_by_id(self, client, sample_invoice_payload):
        create_res = client.post('/api/invoices', data=json.dumps(sample_invoice_payload), content_type='application/json')
        inv_id = create_res.get_json()['invoice']['id']

        response = client.get(f'/api/invoices/{inv_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['invoice']['id'] == inv_id
        assert data['invoice']['customer_name'] == 'Acme Corp'

    def test_get_invoice_not_found(self, client):
        response = client.get('/api/invoices/99999')
        assert response.status_code == 404
        assert 'error' in response.get_json()

    def test_update_invoice(self, client, sample_invoice_payload):
        create_res = client.post('/api/invoices', data=json.dumps(sample_invoice_payload), content_type='application/json')
        inv_id = create_res.get_json()['invoice']['id']

        updated_payload = {
            'customer_name': 'Acme Global Corp',
            'invoice_date': '2026-03-20',
            'gst_percentage': 12.0,
            'items': [
                {
                    'product_name': 'Enterprise Consulting',
                    'quantity': 3,
                    'purchase_price': 100.0,
                    'selling_price': 300.0
                }
            ]
        }

        update_res = client.put(
            f'/api/invoices/{inv_id}',
            data=json.dumps(updated_payload),
            content_type='application/json'
        )
        assert update_res.status_code == 200
        data = update_res.get_json()['invoice']
        assert data['customer_name'] == 'Acme Global Corp'
        assert data['subtotal'] == 900.0
        assert data['gst_percentage'] == 12.0
        assert data['gst_amount'] == 108.0
        assert data['total_amount'] == 1008.0
        assert data['total_cost'] == 300.0
        assert data['profit'] == 600.0
        assert data['profit_margin'] == 66.67
        assert len(data['items']) == 1

    def test_update_invoice_not_found(self, client, sample_invoice_payload):
        response = client.put('/api/invoices/99999', data=json.dumps(sample_invoice_payload), content_type='application/json')
        assert response.status_code == 404

    def test_delete_invoice(self, client, sample_invoice_payload):
        create_res = client.post('/api/invoices', data=json.dumps(sample_invoice_payload), content_type='application/json')
        inv_id = create_res.get_json()['invoice']['id']

        del_res = client.delete(f'/api/invoices/{inv_id}')
        assert del_res.status_code == 200

        # Verify it's gone
        get_res = client.get(f'/api/invoices/{inv_id}')
        assert get_res.status_code == 404

    def test_delete_invoice_not_found(self, client):
        response = client.delete('/api/invoices/99999')
        assert response.status_code == 404
