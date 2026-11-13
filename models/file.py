from pydantic import BaseModel

class CreateFile(BaseModel):
    user_id: int
    filename: str
    filetype: str
    storage_name: str

class File(CreateFile):
    id: int
    created_at: str