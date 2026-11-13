from pydantic import BaseModel

class UsernameUpdate(BaseModel):
    username: str

class CreateUser(BaseModel):
    username: str
    role: str = 'user'

class User(CreateUser):
    id: int