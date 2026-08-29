import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Invoice, InvoiceItem


@pytest.fixture
def app():
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret'
    }
    app = create_app(test_config=test_config)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def sample_invoice_payload():
    return {
        'customer_name': 'Acme Corp',
        'invoice_date': '2026-03-15',
        'gst_percentage': 18.0,
        'items': [
            {
                'product_name': 'Cloud Hosting',
                'quantity': 2,
                'purchase_price': 50.0,
                'selling_price': 100.0
            },
            {
                'product_name': 'Domain Registration',
                'quantity': 1,
                'purchase_price': 10.0,
                'selling_price': 25.0
            }
        ]
    }
