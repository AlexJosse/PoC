# config.py
import os

class Config:
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3356))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'root')
    MYSQL_DB = os.getenv('MYSQL_DB', 'hospital')
    ES_HOST = os.getenv('ES_HOST', 'elasticsearch1')
    ES_PORT = int(os.getenv('ES_PORT', 9200))
    ES_INDEX = os.getenv('ES_INDEX', 'medical_data')
    SFTP_HOST = os.getenv('SFTP_HOST', 'sftp')
    SFTP_PORT = int(os.getenv('SFTP_PORT', 22))
    SFTP_USERNAME = os.getenv('SFTP_USERNAME', 'sftpuser')
    SFTP_PASSWORD = os.getenv('SFTP_PASSWORD', 'password')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/app/uploads')
