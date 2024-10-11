from agent.utils.graph import graph
from models.init_input import InitInput
from models.init_graph import InitGraphInput
from models.init_output import InitOutput
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging

logger = logging.getLogger(name="app")
logging.basicConfig(level=logging.INFO)

load_dotenv()

app = FastAPI()

origins = ["*"]
app.add_middleware(
 CORSMiddleware,
 allow_origins=origins,
 allow_credentials=True,
 allow_methods=["*"],
 allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"status":"ok"}

@app.get("/api/motivations/{user_id}")
def get_motivations(user_id: str = None):
    try:
        result = graph.checkpointer.get_motivation_for_user(user_id)
        return {"message": "Success", "data": result}
    except:
        logger.error("Error getting motivations for user", user_id)
        return {"message": "Error", "data": {}}


@app.post("/api/init")
async def init(input_data: InitInput, background_tasks: BackgroundTasks):
    try:
        thread_id = input_data.get("user_id")
        graph.checkpointer.save_inputs_for_user(user_id=thread_id, role=input_data.get("role_input"), sector=input_data.get("sector_input"))

        logger.info(f"Creating graph with thread ID {thread_id}")
        background_tasks.add_task(process_init_in_background, thread_id, input_data)
        return InitOutput(thread_id=thread_id)
    except Exception as e:
        logger.error(f"Error running graph for thread ID {thread_id}", e)
        return {"message": "Error", "data": {}}

@app.get("/api/graph/{thread_id}")
def get(thread_id: str):
    try:
        config = {"configurable": {"thread_id": thread_id}}
        state = graph.get_state(config)
        result = state[0].get("output")

        if result is not None:
            return {"message": "Success", "data": result}
        return {"message": "Error, graph is not ready yet.", "data": {}}
    except Exception as e:
        logger.error(f"Error getting graph for thread ID {thread_id}", e)
        return {"message": "Error", "data": {}}

def process_init_in_background(thread_id: str, input_data: InitInput):
    try:
        graph.checkpointer.delete_checkpoints_for_thread(thread_id)
        current_resume = graph.checkpointer.get_user_resume(thread_id)
        initial_state = InitGraphInput(
            role_input=input_data.get("role_input"),
            sector_input=input_data.get("sector_input"),
            current_resume=current_resume
        )
        config = {"configurable": {"thread_id": thread_id}}
        graph.invoke(initial_state, config)
        logger.info(f"Created graph with thread ID {thread_id}")
    except Exception as e:
        logger.error(f"Error running graph for thread ID {thread_id}", e)
        return {"message": "Error"}