from datetime import datetime
from typing import List, Dict, Any, Tuple


def calculate_item_values(quantity: int, purchase_price: float, selling_price: float) -> Dict[str, float]:
    """
    Calculate financial values for an individual line item.
    """
    if not isinstance(quantity, (int, float)) or quantity < 0:
        raise ValueError("Quantity cannot be negative")
    if not isinstance(purchase_price, (int, float)) or purchase_price < 0:
        raise ValueError("Purchase price cannot be negative")
    if not isinstance(selling_price, (int, float)) or selling_price < 0:
        raise ValueError("Selling price cannot be negative")

    item_subtotal = float(quantity) * float(selling_price)
    item_cost = float(quantity) * float(purchase_price)
    item_profit = item_subtotal - item_cost

    return {
        'item_subtotal': round(item_subtotal, 2),
        'item_cost': round(item_cost, 2),
        'item_profit': round(item_profit, 2)
    }


def calculate_invoice_totals(items: List[Dict[str, Any]], gst_percentage: float = 0.0) -> Dict[str, float]:
    """
    Calculate consolidated totals for an invoice based on line items and GST rate.
    """
    if gst_percentage < 0 or gst_percentage > 100:
        raise ValueError("GST percentage must be between 0 and 100")

    subtotal = sum(float(item.get('item_subtotal', 0.0)) for item in items)
    total_cost = sum(float(item.get('item_cost', 0.0)) for item in items)

    gst_amount = subtotal * (float(gst_percentage) / 100.0)
    total_amount = subtotal + gst_amount
    profit = subtotal - total_cost

    return {
        'subtotal': round(subtotal, 2),
        'gst_amount': round(gst_amount, 2),
        'total_amount': round(total_amount, 2),
        'total_cost': round(total_cost, 2),
        'profit': round(profit, 2)
    }


def calculate_profit_margin(profit: float, subtotal: float) -> float:
    """
    Calculate profit margin percentage with safe zero-division handling.
    """
    if not subtotal or subtotal <= 0:
        return 0.0
    return round((float(profit) / float(subtotal)) * 100.0, 2)


def validate_invoice_data(data: Dict[str, Any]) -> List[str]:
    """
    Validate incoming invoice dictionary payload. Returns list of error messages.
    """
    errors: List[str] = []

    if not isinstance(data, dict):
        return ["Request body must be a valid JSON object"]

    # Customer Name Validation
    customer_name = data.get('customer_name')
    if not customer_name or not isinstance(customer_name, str) or not customer_name.strip():
        errors.append("Customer name is required and cannot be empty")

    # Invoice Date Validation
    invoice_date_str = data.get('invoice_date')
    if not invoice_date_str:
        errors.append("Invoice date is required")
    else:
        try:
            datetime.strptime(str(invoice_date_str), '%Y-%m-%d')
        except ValueError:
            errors.append("Invoice date must be in YYYY-MM-DD format")

    # GST Validation
    gst = data.get('gst_percentage', 0.0)
    try:
        gst_val = float(gst)
        if gst_val < 0 or gst_val > 100:
            errors.append("GST percentage must be between 0 and 100")
    except (TypeError, ValueError):
        errors.append("GST percentage must be a valid number")

    # Items Validation
    items = data.get('items')
    if not items or not isinstance(items, list) or len(items) == 0:
        errors.append("At least one invoice item is required")
    else:
        for idx, item in enumerate(items, start=1):
            if not isinstance(item, dict):
                errors.append(f"Item {idx}: Must be a JSON object")
                continue

            product_name = item.get('product_name')
            if not product_name or not isinstance(product_name, str) or not product_name.strip():
                errors.append(f"Item {idx}: Product name is required")

            # Quantity
            if 'quantity' not in item:
                errors.append(f"Item {idx}: Quantity is required")
            else:
                try:
                    qty = int(item['quantity'])
                    if qty <= 0:
                        errors.append(f"Item {idx}: Quantity must be greater than 0")
                except (TypeError, ValueError):
                    errors.append(f"Item {idx}: Quantity must be a valid integer")

            # Purchase Price
            if 'purchase_price' not in item:
                errors.append(f"Item {idx}: Purchase price is required")
            else:
                try:
                    pprice = float(item['purchase_price'])
                    if pprice < 0:
                        errors.append(f"Item {idx}: Purchase price cannot be negative")
                except (TypeError, ValueError):
                    errors.append(f"Item {idx}: Purchase price must be a valid number")

            # Selling Price
            if 'selling_price' not in item:
                errors.append(f"Item {idx}: Selling price is required")
            else:
                try:
                    sprice = float(item['selling_price'])
                    if sprice < 0:
                        errors.append(f"Item {idx}: Selling price cannot be negative")
                except (TypeError, ValueError):
                    errors.append(f"Item {idx}: Selling price must be a valid number")

    return errors