from pydantic import BaseModel

class CreateOauthAccount(BaseModel):
    provider: str
    provider_id: str
    provider_email: str

class OauthAccount(CreateOauthAccount):
    id: int
    user_id: int