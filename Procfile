web: gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
release: python -c "from app import create_app, db; app=create_app(); ctx=app.app_context(); ctx.push(); db.create_all(); print('DB tables ready')"

