from typing import Dict, Any, List
from sqlalchemy import func, extract
from app import db
from app.models import Invoice, InvoiceItem


class AnalyticsService:
    @staticmethod
    def get_summary() -> Dict[str, Any]:
        """
        Compute top-level business KPI summary metrics.
        """
        invoices = Invoice.query.all()

        if not invoices:
            return {
                'total_revenue': 0.0,
                'total_cost': 0.0,
                'total_profit': 0.0,
                'total_gst': 0.0,
                'invoice_count': 0,
                'average_invoice_value': 0.0,
                'profit_margin': 0.0
            }

        total_revenue = sum(float(inv.total_amount or 0.0) for inv in invoices)
        total_cost = sum(float(inv.total_cost or 0.0) for inv in invoices)
        total_profit = sum(float(inv.profit or 0.0) for inv in invoices)
        total_gst = sum(float(inv.gst_amount or 0.0) for inv in invoices)
        total_subtotal = sum(float(inv.subtotal or 0.0) for inv in invoices)
        invoice_count = len(invoices)

        avg_invoice_val = total_revenue / invoice_count if invoice_count > 0 else 0.0
        profit_margin = (total_profit / total_subtotal * 100.0) if total_subtotal > 0 else 0.0

        return {
            'total_revenue': round(total_revenue, 2),
            'total_cost': round(total_cost, 2),
            'total_profit': round(total_profit, 2),
            'total_gst': round(total_gst, 2),
            'invoice_count': invoice_count,
            'average_invoice_value': round(avg_invoice_val, 2),
            'profit_margin': round(profit_margin, 2)
        }

    @staticmethod
    def get_monthly_sales() -> List[Dict[str, Any]]:
        """
        Retrieve monthly sales trend and calculate Month-over-Month (MoM) sales growth rates.
        """
        results = db.session.query(
            extract('year', Invoice.invoice_date).label('year'),
            extract('month', Invoice.invoice_date).label('month'),
            func.sum(Invoice.total_amount).label('total_sales'),
            func.count(Invoice.id).label('invoice_count')
        ).group_by(
            extract('year', Invoice.invoice_date),
            extract('month', Invoice.invoice_date)
        ).order_by(
            extract('year', Invoice.invoice_date),
            extract('month', Invoice.invoice_date)
        ).all()

        monthly_data = []
        prev_sales = None

        for r in results:
            sales = round(float(r.total_sales or 0.0), 2)
            year_val = int(r.year)
            month_val = int(r.month)
            month_str = f"{year_val:04d}-{month_val:02d}"

            growth_rate = None
            if prev_sales is not None and prev_sales > 0:
                growth_rate = round(((sales - prev_sales) / prev_sales) * 100.0, 2)

            prev_sales = sales

            monthly_data.append({
                'year': year_val,
                'month': month_val,
                'period': month_str,
                'total_sales': sales,
                'invoice_count': int(r.invoice_count or 0),
                'growth_rate_pct': growth_rate
            })

        return monthly_data

    @staticmethod
    def get_monthly_profit() -> List[Dict[str, Any]]:
        """
        Retrieve monthly profit trends and calculate MoM profit growth rates.
        """
        results = db.session.query(
            extract('year', Invoice.invoice_date).label('year'),
            extract('month', Invoice.invoice_date).label('month'),
            func.sum(Invoice.profit).label('total_profit'),
            func.sum(Invoice.subtotal).label('total_subtotal')
        ).group_by(
            extract('year', Invoice.invoice_date),
            extract('month', Invoice.invoice_date)
        ).order_by(
            extract('year', Invoice.invoice_date),
            extract('month', Invoice.invoice_date)
        ).all()

        monthly_data = []
        prev_profit = None

        for r in results:
            profit = round(float(r.total_profit or 0.0), 2)
            subtotal = float(r.total_subtotal or 0.0)
            year_val = int(r.year)
            month_val = int(r.month)
            month_str = f"{year_val:04d}-{month_val:02d}"

            margin = round((profit / subtotal * 100.0), 2) if subtotal > 0 else 0.0

            growth_rate = None
            if prev_profit is not None and prev_profit != 0:
                growth_rate = round(((profit - prev_profit) / abs(prev_profit)) * 100.0, 2)

            prev_profit = profit

            monthly_data.append({
                'year': year_val,
                'month': month_val,
                'period': month_str,
                'total_profit': profit,
                'profit_margin': margin,
                'profit_growth_pct': growth_rate
            })

        return monthly_data

    @staticmethod
    def get_top_products(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve top products ranked by sales revenue.
        """
        results = db.session.query(
            InvoiceItem.product_name,
            func.sum(InvoiceItem.quantity).label('total_quantity'),
            func.sum(InvoiceItem.item_subtotal).label('total_revenue'),
            func.sum(InvoiceItem.item_profit).label('total_profit')
        ).group_by(
            InvoiceItem.product_name
        ).order_by(
            func.sum(InvoiceItem.item_subtotal).desc()
        ).limit(limit).all()

        return [
            {
                'product_name': r.product_name,
                'total_quantity': int(r.total_quantity or 0),
                'total_revenue': round(float(r.total_revenue or 0.0), 2),
                'total_profit': round(float(r.total_profit or 0.0), 2),
                'profit_margin': round((float(r.total_profit or 0.0) / float(r.total_revenue or 1.0)) * 100.0, 2) if float(r.total_revenue or 0.0) > 0 else 0.0
            }
            for r in results
        ]

    @staticmethod
    def get_most_profitable_products(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve products ranked by total net profit.
        """
        results = db.session.query(
            InvoiceItem.product_name,
            func.sum(InvoiceItem.quantity).label('total_quantity'),
            func.sum(InvoiceItem.item_subtotal).label('total_revenue'),
            func.sum(InvoiceItem.item_profit).label('total_profit')
        ).group_by(
            InvoiceItem.product_name
        ).order_by(
            func.sum(InvoiceItem.item_profit).desc()
        ).limit(limit).all()

        return [
            {
                'product_name': r.product_name,
                'total_quantity': int(r.total_quantity or 0),
                'total_revenue': round(float(r.total_revenue or 0.0), 2),
                'total_profit': round(float(r.total_profit or 0.0), 2),
                'profit_margin': round((float(r.total_profit or 0.0) / float(r.total_revenue or 1.0)) * 100.0, 2) if float(r.total_revenue or 0.0) > 0 else 0.0
            }
            for r in results
        ]

    @staticmethod
    def get_gst_summary() -> List[Dict[str, Any]]:
        """
        Summarize tax liabilities grouped by GST rate slab.
        """
        results = db.session.query(
            Invoice.gst_percentage,
            func.count(Invoice.id).label('invoice_count'),
            func.sum(Invoice.gst_amount).label('total_gst'),
            func.sum(Invoice.subtotal).label('total_subtotal'),
            func.sum(Invoice.total_amount).label('total_amount')
        ).group_by(
            Invoice.gst_percentage
        ).order_by(
            Invoice.gst_percentage
        ).all()

        return [
            {
                'gst_percentage': round(float(r.gst_percentage or 0.0), 2),
                'invoice_count': int(r.invoice_count or 0),
                'total_gst': round(float(r.total_gst or 0.0), 2),
                'total_taxable_subtotal': round(float(r.total_subtotal or 0.0), 2),
                'total_amount_with_tax': round(float(r.total_amount or 0.0), 2)
            }
            for r in results
        ]