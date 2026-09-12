from app import create_app

# Vercel / serverless entrypoint — must expose `app`
app = create_app()
