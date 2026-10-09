from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def hello():
    return {"message": "Hello FastAPI"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {
        "user_id": user_id
    }

@app.get("/users")
def get_users(
    page: int = 1,
    size: int = 10
):
    return {
        "page": page,
        "size": size
    }
