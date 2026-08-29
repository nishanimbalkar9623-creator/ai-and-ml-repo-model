from datetime import datetime
from typing import List, Dict, Any, Optional
from app import db
from app.models import Invoice, InvoiceItem
from app.services.calculation_service import (
    calculate_item_values,
    calculate_invoice_totals,
    validate_invoice_data
)


class InvoiceService:
    @staticmethod
    def create_invoice(data: Dict[str, Any]) -> Invoice:
        """
        Validates invoice data, calculates financials, and creates an invoice with line items.
        """
        errors = validate_invoice_data(data)
        if errors:
            raise ValueError("; ".join(errors))

        items_data = data['items']
        calculated_items = []

        for item_data in items_data:
            calc = calculate_item_values(
                quantity=int(item_data['quantity']),
                purchase_price=float(item_data['purchase_price']),
                selling_price=float(item_data['selling_price'])
            )
            calculated_items.append({**item_data, **calc})

        gst_pct = float(data.get('gst_percentage', 0.0))
        totals = calculate_invoice_totals(calculated_items, gst_percentage=gst_pct)

        invoice_date = datetime.strptime(str(data['invoice_date']), '%Y-%m-%d').date()

        invoice = Invoice(
            customer_name=str(data['customer_name']).strip(),
            invoice_date=invoice_date,
            subtotal=totals['subtotal'],
            gst_percentage=gst_pct,
            gst_amount=totals['gst_amount'],
            total_amount=totals['total_amount'],
            total_cost=totals['total_cost'],
            profit=totals['profit']
        )

        db.session.add(invoice)
        db.session.flush()

        for item_data in calculated_items:
            item = InvoiceItem(
                invoice_id=invoice.id,
                product_name=str(item_data['product_name']).strip(),
                quantity=int(item_data['quantity']),
                purchase_price=float(item_data['purchase_price']),
                selling_price=float(item_data['selling_price']),
                item_subtotal=item_data['item_subtotal'],
                item_cost=item_data['item_cost'],
                item_profit=item_data['item_profit']
            )
            db.session.add(item)

        db.session.commit()
        return invoice

    @staticmethod
    def get_invoice(invoice_id: int) -> Optional[Invoice]:
        """
        Fetch a single invoice by its ID.
        """
        return db.session.get(Invoice, invoice_id)

    @staticmethod
    def get_all_invoices(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        customer_name: Optional[str] = None
    ) -> List[Invoice]:
        """
        Fetch all invoices with optional filtering.
        """
        query = Invoice.query

        if customer_name:
            query = query.filter(Invoice.customer_name.ilike(f"%{customer_name.strip()}%"))

        if start_date:
            try:
                s_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Invoice.invoice_date >= s_date)
            except ValueError:
                pass

        if end_date:
            try:
                e_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Invoice.invoice_date <= e_date)
            except ValueError:
                pass

        return query.order_by(Invoice.invoice_date.desc(), Invoice.id.desc()).all()

    @staticmethod
    def update_invoice(invoice_id: int, data: Dict[str, Any]) -> Optional[Invoice]:
        """
        Update an existing invoice and its line items.
        """
        invoice = db.session.get(Invoice, invoice_id)
        if not invoice:
            return None

        errors = validate_invoice_data(data)
        if errors:
            raise ValueError("; ".join(errors))

        # Clear existing items
        InvoiceItem.query.filter_by(invoice_id=invoice_id).delete()

        items_data = data['items']
        calculated_items = []

        for item_data in items_data:
            calc = calculate_item_values(
                quantity=int(item_data['quantity']),
                purchase_price=float(item_data['purchase_price']),
                selling_price=float(item_data['selling_price'])
            )
            calculated_items.append({**item_data, **calc})

        gst_pct = float(data.get('gst_percentage', 0.0))
        totals = calculate_invoice_totals(calculated_items, gst_percentage=gst_pct)

        invoice_date = datetime.strptime(str(data['invoice_date']), '%Y-%m-%d').date()

        invoice.customer_name = str(data['customer_name']).strip()
        invoice.invoice_date = invoice_date
        invoice.subtotal = totals['subtotal']
        invoice.gst_percentage = gst_pct
        invoice.gst_amount = totals['gst_amount']
        invoice.total_amount = totals['total_amount']
        invoice.total_cost = totals['total_cost']
        invoice.profit = totals['profit']

        for item_data in calculated_items:
            item = InvoiceItem(
                invoice_id=invoice.id,
                product_name=str(item_data['product_name']).strip(),
                quantity=int(item_data['quantity']),
                purchase_price=float(item_data['purchase_price']),
                selling_price=float(item_data['selling_price']),
                item_subtotal=item_data['item_subtotal'],
                item_cost=item_data['item_cost'],
                item_profit=item_data['item_profit']
            )
            db.session.add(item)

        db.session.commit()
        return invoice

    @staticmethod
    def delete_invoice(invoice_id: int) -> bool:
        """
        Delete an invoice and all associated items.
        """
        invoice = db.session.get(Invoice, invoice_id)
        if not invoice:
            return False

        db.session.delete(invoice)
        db.session.commit()
        return True