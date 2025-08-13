import uvicorn

if __name__ == '__main__':
    uvicorn.run('apscheduler_db.main:app', port=8889, host='0.0.0.0')