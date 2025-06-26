import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SWAGGER = {
        'title': 'Asset Manager API',
        'uiversion': 3,
        'version': '1.0',
        'description': "REST API to manage assets with service/expiration time monitoring",
    }
