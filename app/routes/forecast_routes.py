from flask import Blueprint, jsonify, request
from app.services.forecast_service import ForecastService

forecast_bp = Blueprint('forecast', __name__)


@forecast_bp.route('/sales', methods=['GET'])
def get_sales_forecast():
    try:
        months_param = request.args.get('months', default=3, type=int)
        result = ForecastService.forecast_sales(months_ahead=months_param)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Failed to generate sales forecast: {str(e)}'}), 500