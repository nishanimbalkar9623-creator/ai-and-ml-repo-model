from flask import Blueprint, jsonify
from app.services.ai_service import AIService

ai_bp = Blueprint('ai', __name__)


@ai_bp.route('/insights', methods=['POST', 'GET'])
def get_ai_insights():
    try:
        result = AIService.generate_business_insights()
        status_code = 200
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({'error': f'Failed to generate business insights: {str(e)}'}), 500
