import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__)

    # Default configuration
    default_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'invoice.db')
    os.makedirs(os.path.dirname(default_db_path), exist_ok=True)
    default_sqlite_url = f"sqlite:///{default_db_path}"

    database_url = os.getenv('DATABASE_URL', default_sqlite_url)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

    if test_config:
        app.config.update(test_config)

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

    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    return app