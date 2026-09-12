import urllib.request
import json
import os

BASE_URL = f"http://127.0.0.1:{os.getenv('PORT', '8002')}"

def test_api(url, method='GET', data=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Content-Type', 'application/json')
    body = json.dumps(data).encode('utf-8') if data else None
    with urllib.request.urlopen(req, data=body) as res:
        return res.status, json.loads(res.read().decode('utf-8'))

print("=== 1. Health Check ===")
status, res = test_api(f'{BASE_URL}/health')
print(f"Status: {status}, Response: {res}")

print("\n=== 2. Creating Sample Invoices ===")
invoices = [
    {
        'customer_name': 'Apex Corp',
        'invoice_date': '2026-01-15',
        'gst_percentage': 18.0,
        'items': [{'product_name': 'ERP Suite', 'quantity': 2, 'purchase_price': 1000.0, 'selling_price': 2500.0}]
    },
    {
        'customer_name': 'Starlight Ltd',
        'invoice_date': '2026-02-18',
        'gst_percentage': 18.0,
        'items': [{'product_name': 'Cloud Hosting', 'quantity': 5, 'purchase_price': 200.0, 'selling_price': 600.0}]
    },
    {
        'customer_name': 'Quantum AI',
        'invoice_date': '2026-03-22',
        'gst_percentage': 12.0,
        'items': [{'product_name': 'ERP Suite', 'quantity': 3, 'purchase_price': 1000.0, 'selling_price': 2500.0}]
    }
]

for inv in invoices:
    status, res = test_api(f'{BASE_URL}/api/invoices', 'POST', inv)
    inv_data = res['invoice']
    print(f"Created Invoice #{inv_data['id']} for {inv_data['customer_name']}: Total=${inv_data['total_amount']} | Profit=${inv_data['profit']} | Margin={inv_data['profit_margin']}%")

print("\n=== 3. Analytics Summary ===")
status, res = test_api(f'{BASE_URL}/api/analytics/summary')
print(json.dumps(res, indent=2))

print("\n=== 4. Monthly Sales Trend ===")
status, res = test_api(f'{BASE_URL}/api/analytics/monthly-sales')
print(json.dumps(res, indent=2))

print("\n=== 5. Top Products ===")
status, res = test_api(f'{BASE_URL}/api/analytics/top-products')
print(json.dumps(res, indent=2))

print("\n=== 6. Sales Forecast (Next 3 Months) ===")
status, res = test_api(f'{BASE_URL}/api/forecast/sales?months=3')
print(json.dumps(res, indent=2))

print("\n=== 7. AI Executive Insights ===")
status, res = test_api(f'{BASE_URL}/api/ai/insights', 'POST')
print(json.dumps(res, indent=2))
