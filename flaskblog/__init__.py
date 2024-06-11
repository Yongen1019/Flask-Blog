from flask import Flask, render_template

def create_app():
    app = Flask(__name__)
    app.secret_key = 'hday9o32ej382jjdi09hh3'

    # create a route decorator
    @app.route('/')
    def index():
        return "Hello"
    
    # create custom error pages

    # invalid url
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    # internal server error
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app