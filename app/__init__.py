from flask import Flask


def create_app():
    app = Flask(__name__)

    from app.routes import api, download, verify, view

    app.register_blueprint(api.bp)
    app.register_blueprint(download.bp)
    app.register_blueprint(verify.bp)
    app.register_blueprint(view.bp)

    return app
