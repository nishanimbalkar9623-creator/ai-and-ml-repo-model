from datetime import datetime, timezone
from app import db


class Invoice(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(255), nullable=False, index=True)
    invoice_date = db.Column(db.Date, nullable=False, index=True)
    subtotal = db.Column(db.Float, nullable=False, default=0.0)
    gst_percentage = db.Column(db.Float, nullable=False, default=0.0)
    gst_amount = db.Column(db.Float, nullable=False, default=0.0)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    total_cost = db.Column(db.Float, nullable=False, default=0.0)
    profit = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    items = db.relationship(
        'InvoiceItem',
        backref='invoice',
        lazy=True,
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    def to_dict(self):
        profit_margin = round((self.profit / self.subtotal * 100), 2) if self.subtotal and self.subtotal > 0 else 0.0
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'invoice_date': self.invoice_date.isoformat() if self.invoice_date else None,
            'subtotal': round(float(self.subtotal or 0.0), 2),
            'gst_percentage': round(float(self.gst_percentage or 0.0), 2),
            'gst_amount': round(float(self.gst_amount or 0.0), 2),
            'total_amount': round(float(self.total_amount or 0.0), 2),
            'total_cost': round(float(self.total_cost or 0.0), 2),
            'profit': round(float(self.profit or 0.0), 2),
            'profit_margin': profit_margin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'items': [item.to_dict() for item in self.items]
        }

    def __repr__(self):
        return f'<Invoice id={self.id} customer="{self.customer_name}" total={self.total_amount}>'