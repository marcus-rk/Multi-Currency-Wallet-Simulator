import os

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
	DATABASE = os.path.join(os.getcwd(), 'instance', 'wallet.db')
	API_BASE_PATH = '/api'

class TestConfig(Config):
	TESTING = True
	DATABASE = os.path.join(os.getcwd(), 'instance', 'test_wallet.db')