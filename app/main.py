from fastapi import FastAPI

from app.routers.patient import router as patient_router

app = FastAPI()

app.include_router(patient_router)


@app.get("/")
def root():

    return {"message": "ERP API Running"}