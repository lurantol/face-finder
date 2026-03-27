from bootstrap import bootstrap
from ui import create_app

if __name__ == "__main__":
    bootstrap()
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
