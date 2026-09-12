import os
from app import create_app

app = create_app()

def handler(event, context):
    from serverless_wsgi import handle_request
    return handle_request(app, event, context)
