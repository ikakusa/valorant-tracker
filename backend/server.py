from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from pyvaloapi import ValorantClient
import Src.Utils.utils as common

util = common.utils

app = FastAPI()

# class Input(BaseModel):
#     text: str

# @app.post("/process")
# def process(data: Input):
#     result = data.text.upper()
#     return {"result": result}

@app.get("/get-game-state")
def get_game_state():
    result = util.game_state
    return {"result": result }

@app.get("/get-match-data")
def get_match_data():
    return {"result": util.match_data}

@app.get("/get-pregame-data")
def get_match_data():
    return {"result": util.pregame_data}

@app.get("/get-current-match-id")
def get_current_match_id():
    return {"result": util.api.get_current_match_id()}

@app.get("/get-current-pregame-id")
def get_current_pregame_id():
    return {"result": util.api.get_current_pregame_id()}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)