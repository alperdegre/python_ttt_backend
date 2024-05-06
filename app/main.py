from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.engine.engine import GameEngine
from app.routers import auth, lobby

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(lobby.router)

@app.get("/hello-world")
async def root():
    return {"message":"Hello World"}

@app.get("/")
async def route():
    engine = GameEngine()

    print(engine.lobbies)

    lobby, code = engine.create_lobby("test")

    print(engine.lobbies[code].users)

    lobby.join("test2")

    print(engine.lobbies[code].users)