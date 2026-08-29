from flask import Blueprint, request, jsonify
from app.services.invoice_service import InvoiceService

invoice_bp = Blueprint('invoice', __name__)


@invoice_bp.route('', methods=['POST'])
def create_invoice():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Invalid or missing JSON request body'}), 400

        invoice = InvoiceService.create_invoice(data)
        return jsonify({
            'message': 'Invoice created successfully',
            'invoice': invoice.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to create invoice: {str(e)}'}), 500


@invoice_bp.route('', methods=['GET'])
def get_invoices():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        customer_name = request.args.get('customer_name')

        invoices = InvoiceService.get_all_invoices(
            start_date=start_date,
            end_date=end_date,
            customer_name=customer_name
        )
        return jsonify({
            'count': len(invoices),
            'invoices': [inv.to_dict() for inv in invoices]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve invoices: {str(e)}'}), 500


@invoice_bp.route('/<int:invoice_id>', methods=['GET'])
def get_invoice(invoice_id: int):
    try:
        invoice = InvoiceService.get_invoice(invoice_id)
        if not invoice:
            return jsonify({'error': f'Invoice with ID {invoice_id} not found'}), 404
        return jsonify({
            'invoice': invoice.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve invoice: {str(e)}'}), 500


@invoice_bp.route('/<int:invoice_id>', methods=['PUT'])
def update_invoice(invoice_id: int):
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Invalid or missing JSON request body'}), 400

        invoice = InvoiceService.update_invoice(invoice_id, data)
        if not invoice:
            return jsonify({'error': f'Invoice with ID {invoice_id} not found'}), 404
        return jsonify({
            'message': 'Invoice updated successfully',
            'invoice': invoice.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to update invoice: {str(e)}'}), 500


@invoice_bp.route('/<int:invoice_id>', methods=['DELETE'])
def delete_invoice(invoice_id: int):
    try:
        success = InvoiceService.delete_invoice(invoice_id)
        if not success:
            return jsonify({'error': f'Invoice with ID {invoice_id} not found'}), 404
        return jsonify({'message': f'Invoice {invoice_id} deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to delete invoice: {str(e)}'}), 500