from models import User, OauthAccount, CreateUser, CreateOauthAccount, PendingRegistration, CreatePendingRegistration
from db import database
import hashlib

async def record_logout(user: User) -> bool:
    return await database.log_activity(
        user_id=user.id,
        action="logout",
        details="User logged out"
    )

async def record_login(user: User) -> bool:
    return await database.log_activity(
        user_id=user.id,
        action="login",
        details="User logged in"
    )

async def get_oauth_account(provider: str, provider_id: str) -> OauthAccount | None:
    return await database.get_oauth_account(
        provider,
        provider_id
    )

async def get_oauth_accounts(user: User) -> list[OauthAccount]:
    return await database.get_oauth_accounts_by_user_id(user.id)

async def link_oauth_account(user: User, create_oauth_account: CreateOauthAccount) -> OauthAccount:
    oauth_account = await database.link_oauth_account(user, create_oauth_account)

    await database.log_activity(
        user_id=oauth_account.user_id,
        action="Oauth Link",
        details=f"User linked with {oauth_account.provider} Oauth"
    )

    return oauth_account

async def register_user(create_user: CreateUser, create_oauth_account: CreateOauthAccount) -> tuple[User, OauthAccount]:
    user, oauth_account = await database.create_user_with_oauth(create_user, create_oauth_account)

    await database.log_activity(
        user_id=user.id,
        action="register",
        details="User registered a new account"
    )

    return user, oauth_account

async def create_pending_registration(token: str, create_pending: CreatePendingRegistration) -> PendingRegistration:
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return await database.create_pending_registration(token_hash, create_pending)

async def find_pending_registration(token: str) -> PendingRegistration | None:
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return await database.find_pending_registration(token_hash=token_hash)

async def delete_pending_registration(token_hash: str) -> bool:
    return await database.delete_pending_registration(token_hash)

async def check_matching_email(provider_email) -> bool:
    match_id = await database.get_user_id_by_provider_email(provider_email)
    return match_id is not None