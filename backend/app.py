from flask import Flask
from flask_cors import CORS
from config import Config

from routes.public_routes import public_bp
from routes.admin_routes import admin_bp
from routes.staff_routes import staff_bp
from routes.category_routes import category_bp
from routes.department_routes import dept_bp
from routes.notification_routes import notif_bp
from routes.auth_routes import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app)
    
    # Register Blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(dept_bp)
    app.register_blueprint(notif_bp)
    app.register_blueprint(auth_bp)
    
    @app.route('/')
    def index():
        return "Public Complaint Management System API is Running!"
        
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
