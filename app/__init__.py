import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__)

    # Default configuration — absolute path so it works no matter the cwd.
    # NOTE: absolute SQLite URLs need forward slashes: sqlite:///C:/path/to.db
    def _sqlite_url(abs_path: str) -> str:
        abs_path = os.path.abspath(abs_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        return 'sqlite:///' + abs_path.replace(os.sep, '/')

    default_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'invoice.db')
    default_sqlite_url = _sqlite_url(default_db_path)

    database_url = (os.getenv('DATABASE_URL', default_sqlite_url) or '').strip()
    # Allow a plain relative sqlite path in .env too (sqlite:///data/invoice.db), and preserve :memory:
    if database_url.startswith('sqlite:'):
        if ':memory:' in database_url:
            database_url = 'sqlite:///:memory:'
        else:
            path_part = database_url[len('sqlite:'):]
            while path_part.startswith('/'):
                path_part = path_part[1:]
            if not os.path.isabs(path_part) and not (len(path_part) >= 2 and path_part[1] == ':'):
                path_part = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), path_part)
            database_url = _sqlite_url(path_part)
    elif database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

    if test_config:
        app.config.update(test_config)

    # Allow cross-origin requests (needed when frontend / hosted demo calls the API)
    CORS(app)

    # Allow both /api/invoices and /api/invoices/ (Flask strict_slashes fix —
    # previously POST /api/invoices/ returned 308 redirect / CORS preflight issues)
    app.url_map.strict_slashes = False

    db.init_app(app)

    with app.app_context():
        # Import models so tables are registered
        from app.models import Invoice, InvoiceItem  # noqa: F401
        try:
            db.create_all()
        except Exception as e:
            app.logger.warning(f"Could not automatically create all tables: {e}")

    # Register blueprints
    from app.routes.invoice_routes import invoice_bp
    from app.routes.analytics_routes import analytics_bp
    from app.routes.forecast_routes import forecast_bp
    from app.routes.ai_routes import ai_bp

    app.register_blueprint(invoice_bp, url_prefix='/api/invoices')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(forecast_bp, url_prefix='/api/forecast')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')

    @app.route('/')
    def index():
        return jsonify({
            'name': 'AI Invoice, Business Analytics & Sales Forecasting API',
            'status': 'running',
            'docs': '/health — GET server & DB health; /api/invoices, /api/analytics/*, /api/forecast/sales, /api/ai/insights',
            'endpoints': [
                'GET /health',
                'POST /api/invoices',
                'GET /api/invoices',
                'GET /api/invoices/<id>',
                'PUT /api/invoices/<id>',
                'DELETE /api/invoices/<id>',
                'GET /api/analytics/summary',
                'GET /api/analytics/monthly-sales',
                'GET /api/analytics/monthly-profit',
                'GET /api/analytics/top-products',
                'GET /api/analytics/most-profitable-products',
                'GET /api/analytics/gst-summary',
                'GET /api/forecast/sales?months=3',
                'POST /api/ai/insights',
            ],
        }), 200

    @app.route('/health')
    def health_check():
        # Actually verify the DB connection instead of always reporting "connected"
        try:
            db.session.execute(text('SELECT 1'))
            db_status = 'connected'
        except Exception as e:
            app.logger.warning(f"Health-check DB ping failed: {e}")
            db_status = f'disconnected: {e}'
            return jsonify({'status': 'degraded', 'database': db_status}), 500
        return jsonify({
            'status': 'healthy',
            'database': db_status
        }), 200

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        return jsonify({'error': 'Method not allowed for this endpoint'}), 405

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

    return app
