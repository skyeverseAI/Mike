from fastapi import FastAPI

app = FastAPI(title='Mike Legal AI')

@app.get('/health')
def health():
    return {'status':'OK'}