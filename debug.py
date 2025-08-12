import uvicorn

if __name__ == '__main__':
    from apscheduler_db.main import start_instance

    app = start_instance()
    uvicorn.run(app, port=8889, host='0.0.0.0')