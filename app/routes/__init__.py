from app.routes.auth import auth_bp
from app.routes.user import user_bp
from app.routes.admin import admin_bp
from app.routes.webhook import webhook_bp

__all__ = [
    "auth_bp", 
    "user_bp", 
    "admin_bp", 
    "webhook_bp"
]