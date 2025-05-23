from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from users import controller as user_controller
from term import controller as term_controller


app = FastAPI()

origin = ["http://localhost:3000", "http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(user_controller.controller, prefix="/users", tags=["User"])
app.include_router(term_controller.controller, prefix="/terms", tags=["Term"])
