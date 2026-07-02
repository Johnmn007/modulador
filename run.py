import os
from app import create_app

config_name = os.getenv("FLASK_CONFIG", os.getenv("FLASK_ENV", "development"))
app = create_app(config_name)

if __name__ == '__main__':
    debug = config_name == "development"
    app.run(debug=debug)
