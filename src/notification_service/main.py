from fastapi import FastAPI

from notification_service.api.notification import router
from notification_service.database import Base, engine

Base.metadata.create_all(engine)
app = FastAPI()

app.include_router(router)
