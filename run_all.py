import subprocess
import sys
import json
import os
import urllib.request
import time

BASE_PORT = int(os.getenv('PORT', '8002'))
BASE_URL = f"http://127.0.0.1:{BASE_PORT}"

def print_banner(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def run_pytest():
    print_banner("1. RUNNING PYTEST TEST SUITE ACROSS ALL MODULES")
    cmd = [sys.executable, "-m", "pytest", "-v"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0

def test_api(url, method='GET', data=None, timeout=15):
    req = urllib.request.Request(url, method=method)
    req.add_header('Content-Type', 'application/json')
    body = json.dumps(data).encode('utf-8') if data else None
    try:
        with urllib.request.urlopen(req, data=body, timeout=timeout) as res:
            return res.status, json.loads(res.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        try:
            err_body = json.loads(e.read().decode('utf-8'))
        except Exception:
            err_body = {'error': f'HTTP {e.code}'}
        print(f"  ! HTTP {e.code} on {method} {url} -> {err_body}")
        raise
    except urllib.error.URLError as e:
        print(f"  ! Cannot reach server at {url}. Is `python run.py` running on {BASE_URL}? ({e.reason})")
        raise SystemExit(1)

def wait_for_server(retries=15, delay=2):
    for i in range(retries):
        try:
            with urllib.request.urlopen(f"{BASE_URL}/health", timeout=5) as res:
                if res.status == 200:
                    return True
        except Exception:
            pass
        print(f"  ... waiting for server {BASE_URL} ({i + 1}/{retries})")
        time.sleep(delay)
    print(f"  ! Server not reachable at {BASE_URL} after {retries * delay}s. Start it with `python run.py` first.")
    raise SystemExit(1)

def run_live_api_demonstration():
    print_banner(f"2. RUNNING LIVE API DEMONSTRATION ON {BASE_URL}")
    base_url = BASE_URL
    wait_for_server()

    # Step 1: Health Check
    status, res = test_api(f"{base_url}/health")
    print(f"[HEALTH CHECK] Status: {status} | Response: {res}")

    # Step 2: Ingest Invoices
    print("\n--- A. Creating Invoices Across Billing Quarters ---")
    invoices = [
        {
            'customer_name': 'Acme Enterprise Solutions',
            'invoice_date': '2026-01-15',
            'gst_percentage': 18.0,
            'items': [
                {'product_name': 'ERP Core License', 'quantity': 2, 'purchase_price': 1200.0, 'selling_price': 3000.0},
                {'product_name': 'Implementation Consulting', 'quantity': 20, 'purchase_price': 40.0, 'selling_price': 150.0}
            ]
        },
        {
            'customer_name': 'Nexus Digital Media',
            'invoice_date': '2026-02-20',
            'gst_percentage': 18.0,
            'items': [
                {'product_name': 'Cloud Dedicated Servers', 'quantity': 4, 'purchase_price': 350.0, 'selling_price': 900.0},
                {'product_name': 'Domain & SSL Bundles', 'quantity': 10, 'purchase_price': 15.0, 'selling_price': 50.0}
            ]
        },
        {
            'customer_name': 'Starlight Fintech',
            'invoice_date': '2026-03-10',
            'gst_percentage': 12.0,
            'items': [
                {'product_name': 'Cybersecurity Audit', 'quantity': 1, 'purchase_price': 800.0, 'selling_price': 2500.0},
                {'product_name': 'Cloud Dedicated Servers', 'quantity': 6, 'purchase_price': 350.0, 'selling_price': 900.0}
            ]
        },
        {
            'customer_name': 'Quantum Robotics',
            'invoice_date': '2026-04-05',
            'gst_percentage': 18.0,
            'items': [
                {'product_name': 'ERP Core License', 'quantity': 3, 'purchase_price': 1200.0, 'selling_price': 3000.0},
                {'product_name': 'Cybersecurity Audit', 'quantity': 2, 'purchase_price': 800.0, 'selling_price': 2500.0}
            ]
        }
    ]

    created_invoices = []
    for inv_payload in invoices:
        status, res = test_api(f"{base_url}/api/invoices", 'POST', inv_payload)
        inv = res['invoice']
        created_invoices.append(inv)
        print(f"  + Invoice #{inv['id']:02d} | Customer: {inv['customer_name']:<25} | Date: {inv['invoice_date']} | "
              f"Subtotal: ${inv['subtotal']:>8.2f} | GST: ${inv['gst_amount']:>7.2f} | "
              f"Total: ${inv['total_amount']:>8.2f} | Profit: ${inv['profit']:>8.2f} | Margin: {inv['profit_margin']:>5.2f}%")

    # Step 3: Analytics Summary
    print("\n--- B. Executive KPI Summary (/api/analytics/summary) ---")
    status, summary = test_api(f"{base_url}/api/analytics/summary")
    print(f"  Total Invoices Created : {summary['invoice_count']}")
    print(f"  Total Gross Revenue    : ${summary['total_revenue']:,.2f}")
    print(f"  Total Cost of Goods    : ${summary['total_cost']:,.2f}")
    print(f"  Net Operating Profit   : ${summary['total_profit']:,.2f}")
    print(f"  Total GST Collected    : ${summary['total_gst']:,.2f}")
    print(f"  Average Invoice Value  : ${summary['average_invoice_value']:,.2f}")
    print(f"  Consolidated Margin    : {summary['profit_margin']:.2f}%")

    # Step 4: Monthly Sales & Profit Trends
    print("\n--- C. Monthly Sales & Profit Progression (/api/analytics/monthly-sales & monthly-profit) ---")
    _, sales_data = test_api(f"{base_url}/api/analytics/monthly-sales")
    _, profit_data = test_api(f"{base_url}/api/analytics/monthly-profit")
    
    print(f"  {'Period':<10} {'Sales Total':<14} {'MoM Sales Growth':<18} {'Profit Total':<14} {'Margin':<10}")
    print("  " + "-" * 68)
    for s, p in zip(sales_data['monthly_sales'], profit_data['monthly_profit']):
        growth_str = f"{s['growth_rate_pct']:+.1f}%" if s['growth_rate_pct'] is not None else "Baseline"
        print(f"  {s['period']:<10} ${s['total_sales']:>10.2f}   {growth_str:<18} ${p['total_profit']:>10.2f}   {p['profit_margin']:>6.2f}%")

    # Step 5: Top Products
    print("\n--- D. Top Revenue & Profitable Products (/api/analytics/top-products) ---")
    _, top_prods = test_api(f"{base_url}/api/analytics/top-products?limit=5")
    for idx, prod in enumerate(top_prods['top_products'], start=1):
        print(f"  #{idx} {prod['product_name']:<28} | Qty Sold: {prod['total_quantity']:>3} | Revenue: ${prod['total_revenue']:>9.2f} | Profit: ${prod['total_profit']:>8.2f} | Margin: {prod['profit_margin']:.2f}%")

    # Step 6: GST Tax Slabs
    print("\n--- E. GST Tax Slab Breakdown (/api/analytics/gst-summary) ---")
    _, gst_data = test_api(f"{base_url}/api/analytics/gst-summary")
    for g in gst_data['gst_summary']:
        print(f"  GST {g['gst_percentage']:>4.1f}% Slab | Invoices: {g['invoice_count']:>2} | Taxable Subtotal: ${g['total_taxable_subtotal']:>9.2f} | GST Tax Collected: ${g['total_gst']:>8.2f}")

    # Step 7: Sales Forecasting (handles sparse-data gracefully)
    print("\n--- F. Machine Learning Sales Forecast (/api/forecast/sales?months=3) ---")
    _, fc = test_api(f"{base_url}/api/forecast/sales?months=3")
    if fc.get('status') == 'insufficient_data':
        print(f"  ! Forecasting skipped: {fc.get('message')}")
    else:
        print(f"  Model Employed  : {fc['model_type']}")
        print(f"  Trend Direction : {fc['trend_direction'].upper()} ({fc['slope_per_month']:+,.2f}/month)")
        print(f"  Historical Base : {fc['historical_periods_used']} months")
        print("  Projections:")
        for item in fc['forecast']:
            print(f"    * {item['period']} -> Projected: ${item['predicted_sales']:>9.2f}  (90% Conf: ${item['lower_bound']:>9.2f} to ${item['upper_bound']:>9.2f})")

    # Step 8: Gemini AI Insights (handles no-data gracefully)
    print("\n--- G. Gemini AI Executive Insights (/api/ai/insights) ---")
    _, ai_res = test_api(f"{base_url}/api/ai/insights", 'POST')
    if not ai_res.get('insights'):
        print(f"  ! AI insights skipped: {ai_res.get('message', ai_res)}")
    else:
        insights = ai_res['insights']
        print(f"  [EXECUTIVE SUMMARY]\n  {insights['executive_summary']}\n")
        print("  [KEY OBSERVATIONS]")
        for obs in insights['key_observations']:
            print(f"   * {obs}")
        print("\n  [IDENTIFIED BUSINESS RISKS]")
        for risk in insights['business_risks']:
            print(f"   ! {risk}")
        print("\n  [GROWTH OPPORTUNITIES]")
        for opp in insights['growth_opportunities']:
            print(f"   + {opp}")
        print("\n  [ACTIONABLE CFO RECOMMENDATIONS]")
        for rec in insights['actionable_recommendations']:
            print(f"   > {rec}")

    print_banner("ALL CHECKS & DEMONSTRATIONS COMPLETED SUCCESSFULLY")

if __name__ == '__main__':
    tests_ok = run_pytest()
    if tests_ok:
        run_live_api_demonstration()
    else:
        print("\n! Pytest failed — live demo skipped. Fix failing tests first.")
        sys.exit(1)
