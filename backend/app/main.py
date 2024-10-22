from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database.connection import init_db, close_db, engine
from routes.users import user_router
from routes.rooms import room_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db(engine)
    yield
    await close_db(engine)

app = FastAPI(lifespan=lifespan)

origins = [
    'http://localhost:3000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/api/v1/user")
app.include_router(room_router, prefix="/api/v1/room")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
