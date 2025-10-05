from datetime import datetime
from typing import Union
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def read_root():
    now = datetime.now()
    return {"date": now.date().isoformat(), "time": now.time().isoformat() }

