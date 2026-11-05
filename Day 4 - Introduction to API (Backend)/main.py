from fastapi import FastAPI

# Initializes the main FastAPI application instance.
app = FastAPI(
    title="Assignment API",
    description="A simple FastAPI application tracking path and query parameter inputs."
)

@app.get("/")
def read_root():
    # Returns a standard welcome message dictionary serialized automatically into JSON text.
    return {
        "status": "success",
        "message": "Welcome to your first FastAPI application backend server!"
    }

@app.get("/greet/{name}")
def greet_user(name: str, greeting: str = "Hello"):
    # Accepts a dynamic path parameter (name) and an optional query parameter (greeting).
    # Navigating to /greet/Pradeepraj?greeting=Welcome captures both values dynamically.
    return {
        "path_parameter_captured": name,
        "query_parameter_captured": greeting,
        "final_output": f"{greeting}, {name}!"
    }



