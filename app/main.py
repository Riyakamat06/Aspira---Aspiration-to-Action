from fastapi import FastAPI

app = FastAPI(title="Aspira - Aspiration to Action")

@app.get("/health")
def health():
    return {"status": "ok"}
