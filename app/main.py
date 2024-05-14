from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, game, lobby

app = FastAPI()

origins = ['https://tictactoe.alperdegre.com','https://ttt.alperdegre.com']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(lobby.router)
app.include_router(game.router)

@app.get("/hello-world")
async def root():
    return {"message":"Hello World"}