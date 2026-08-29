import pytest
from app.services.calculation_service import (
    calculate_item_values,
    calculate_invoice_totals,
    calculate_profit_margin,
    validate_invoice_data
)


class TestCalculationService:
    def test_calculate_item_values_normal(self):
        result = calculate_item_values(quantity=5, purchase_price=40.0, selling_price=60.0)
        assert result['item_subtotal'] == 300.0
        assert result['item_cost'] == 200.0
        assert result['item_profit'] == 100.0

    def test_calculate_item_values_zero_cost(self):
        result = calculate_item_values(quantity=2, purchase_price=0.0, selling_price=50.0)
        assert result['item_subtotal'] == 100.0
        assert result['item_cost'] == 0.0
        assert result['item_profit'] == 100.0

    def test_calculate_item_values_negative_quantity_raises(self):
        with pytest.raises(ValueError, match="Quantity cannot be negative"):
            calculate_item_values(quantity=-1, purchase_price=10.0, selling_price=20.0)

    def test_calculate_item_values_negative_prices_raises(self):
        with pytest.raises(ValueError, match="Purchase price cannot be negative"):
            calculate_item_values(quantity=1, purchase_price=-5.0, selling_price=20.0)

        with pytest.raises(ValueError, match="Selling price cannot be negative"):
            calculate_item_values(quantity=1, purchase_price=5.0, selling_price=-20.0)

    def test_calculate_invoice_totals(self):
        items = [
            {'item_subtotal': 200.0, 'item_cost': 120.0, 'item_profit': 80.0},
            {'item_subtotal': 50.0, 'item_cost': 30.0, 'item_profit': 20.0}
        ]
        # 18% GST on subtotal of 250.0 = 45.0
        totals = calculate_invoice_totals(items, gst_percentage=18.0)
        assert totals['subtotal'] == 250.0
        assert totals['gst_amount'] == 45.0
        assert totals['total_amount'] == 295.0
        assert totals['total_cost'] == 150.0
        assert totals['profit'] == 100.0

    def test_calculate_invoice_totals_invalid_gst(self):
        items = [{'item_subtotal': 100.0, 'item_cost': 50.0, 'item_profit': 50.0}]
        with pytest.raises(ValueError, match="GST percentage must be between 0 and 100"):
            calculate_invoice_totals(items, gst_percentage=105.0)

        with pytest.raises(ValueError, match="GST percentage must be between 0 and 100"):
            calculate_invoice_totals(items, gst_percentage=-5.0)

    def test_calculate_profit_margin(self):
        assert calculate_profit_margin(profit=50.0, subtotal=200.0) == 25.0
        assert calculate_profit_margin(profit=0.0, subtotal=100.0) == 0.0
        assert calculate_profit_margin(profit=10.0, subtotal=0.0) == 0.0

    def test_validate_invoice_data_valid(self):
        payload = {
            'customer_name': 'Tech Solutions',
            'invoice_date': '2026-03-01',
            'gst_percentage': 18.0,
            'items': [
                {'product_name': 'Server Setup', 'quantity': 1, 'purchase_price': 500.0, 'selling_price': 800.0}
            ]
        }
        errors = validate_invoice_data(payload)
        assert len(errors) == 0

    def test_validate_invoice_data_invalid_fields(self):
        payload = {
            'customer_name': '',
            'invoice_date': 'invalid-date',
            'gst_percentage': 150.0,
            'items': []
        }
        errors = validate_invoice_data(payload)
        assert any("Customer name is required" in e for e in errors)
        assert any("YYYY-MM-DD" in e for e in errors)
        assert any("GST percentage must be between 0 and 100" in e for e in errors)
        assert any("At least one invoice item is required" in e for e in errors)

    def test_validate_invoice_data_invalid_item_values(self):
        payload = {
            'customer_name': 'Client A',
            'invoice_date': '2026-03-01',
            'gst_percentage': 5.0,
            'items': [
                {'product_name': '', 'quantity': 0, 'purchase_price': -10.0, 'selling_price': -20.0}
            ]
        }
        errors = validate_invoice_data(payload)
        assert any("Product name is required" in e for e in errors)
        assert any("Quantity must be greater than 0" in e for e in errors)
        assert any("Purchase price cannot be negative" in e for e in errors)
        assert any("Selling price cannot be negative" in e for e in errors)
