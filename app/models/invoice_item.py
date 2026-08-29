from app import db


class InvoiceItem(db.Model):
    __tablename__ = 'invoice_items'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(
        db.Integer,
        db.ForeignKey('invoices.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    product_name = db.Column(db.String(255), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    item_subtotal = db.Column(db.Float, nullable=False, default=0.0)
    item_cost = db.Column(db.Float, nullable=False, default=0.0)
    item_profit = db.Column(db.Float, nullable=False, default=0.0)

    def to_dict(self):
        subtotal = float(self.item_subtotal or 0.0)
        profit = float(self.item_profit or 0.0)
        profit_margin = round((profit / subtotal * 100), 2) if subtotal > 0 else 0.0

        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'purchase_price': round(float(self.purchase_price or 0.0), 2),
            'selling_price': round(float(self.selling_price or 0.0), 2),
            'item_subtotal': round(subtotal, 2),
            'item_cost': round(float(self.item_cost or 0.0), 2),
            'item_profit': round(profit, 2),
            'item_profit_margin': profit_margin
        }

    def __repr__(self):
        return f'<InvoiceItem id={self.id} product="{self.product_name}" qty={self.quantity}>'
