from flask import Flask, render_template

def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/rename")
    def rename():
        return render_template("rename.html")

    @app.route("/search")
    def search():
        return render_template("search.html")

    @app.route("/upload")
    def upload():
        return render_template("upload.html")

    return app
