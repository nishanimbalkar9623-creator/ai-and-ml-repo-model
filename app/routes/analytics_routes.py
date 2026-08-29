from flask import Blueprint, jsonify, request
from app.services.analytics_service import AnalyticsService

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/summary', methods=['GET'])
def get_analytics_summary():
    try:
        summary = AnalyticsService.get_summary()
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve analytics summary: {str(e)}'}), 500


@analytics_bp.route('/monthly-sales', methods=['GET'])
def get_monthly_sales():
    try:
        data = AnalyticsService.get_monthly_sales()
        return jsonify({
            'count': len(data),
            'monthly_sales': data
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve monthly sales: {str(e)}'}), 500


@analytics_bp.route('/monthly-profit', methods=['GET'])
def get_monthly_profit():
    try:
        data = AnalyticsService.get_monthly_profit()
        return jsonify({
            'count': len(data),
            'monthly_profit': data
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve monthly profit: {str(e)}'}), 500


@analytics_bp.route('/top-products', methods=['GET'])
def get_top_products():
    try:
        limit = request.args.get('limit', 10, type=int)
        data = AnalyticsService.get_top_products(limit=limit)
        return jsonify({
            'count': len(data),
            'top_products': data
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve top products: {str(e)}'}), 500


@analytics_bp.route('/most-profitable-products', methods=['GET'])
def get_most_profitable_products():
    try:
        limit = request.args.get('limit', 10, type=int)
        data = AnalyticsService.get_most_profitable_products(limit=limit)
        return jsonify({
            'count': len(data),
            'profitable_products': data
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve profitable products: {str(e)}'}), 500


@analytics_bp.route('/gst-summary', methods=['GET'])
def get_gst_summary():
    try:
        data = AnalyticsService.get_gst_summary()
        return jsonify({
            'count': len(data),
            'gst_summary': data
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve GST summary: {str(e)}'}), 500