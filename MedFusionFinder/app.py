# app.py
import os
import sys
import logging
from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Configure logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from routes.main import main as main_blueprint
app.register_blueprint(main_blueprint)

from routes.sftp import sftp_bp as sftp_blueprint
app.register_blueprint(sftp_blueprint)

from routes.search import search_bp as search_blueprint
app.register_blueprint(search_blueprint)


from routes.database import db_bp as db_blueprint
app.register_blueprint(db_blueprint)

from routes.upload import upload_bp as upload_blueprint
app.register_blueprint(upload_blueprint)

from routes.csv import csv_bp as csv_blueprint
app.register_blueprint(csv_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
