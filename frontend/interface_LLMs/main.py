from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from llms import query_occupancy_with_instruction_model, generate_instruction_response
import gc
import torch

# garbage collection and emptying cache
gc.collect()

# Clear GPU memory
if torch.cuda.is_available():
    torch.cuda.empty_cache()

app = FastAPI()

class QueryModel(BaseModel):
    time: datetime
    room_id: int

@app.post("/query_occupancy")
async def query_occupancy(query: QueryModel):
    criteria = {
        "time": query.time,
        "room_id": query.room_id,
    }
    # Check if the criteria specify a room and if the room is empty
    if 'room_id' in criteria and criteria['room_id'] == 0:
        del criteria['room_id']
        
    response = query_occupancy_with_instruction_model(criteria)
    return {"response": response}

@app.get("/")
async def root():
    return {"message": "Welcome to the occupancy query service!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/chat")
async def chat(prompt: str):
    response = generate_instruction_response(prompt)
    return {"message": response}