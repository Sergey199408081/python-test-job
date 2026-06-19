from sanic import Sanic
from sanic.response import json
from app.routes import (
    auth_bp, 
    user_bp, 
    admin_bp, 
    webhook_bp
)
from app.database import init_db, close_db, init_engine
from app.config import settings


def create_app(database_url: str = None) -> Sanic:
    app = Sanic("PaymentAPI")
    
    app.blueprint(auth_bp)
    app.blueprint(user_bp)
    app.blueprint(admin_bp)
    app.blueprint(webhook_bp)
    
    @app.listener("before_server_start")
    async def setup_db(app, loop):
        init_engine(database_url)
        await init_db()
    
    @app.listener("after_server_stop")
    async def close_db_connection(app, loop):
        await close_db()
    
    @app.get("/health")
    async def health(request):
        return json({"status": "ok"})
    
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=settings.APP_HOST, port=settings.APP_PORT, debug=settings.DEBUG)