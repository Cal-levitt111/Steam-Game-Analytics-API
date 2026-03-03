import os


def pytest_sessionstart(session):
    os.environ.setdefault('SECRET_KEY', 'test-secret-key')
    os.environ.setdefault('ACCESS_TOKEN_EXPIRE_MINUTES', '1440')
    os.environ.setdefault('ENVIRONMENT', 'test')