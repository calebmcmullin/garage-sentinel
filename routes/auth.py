from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from models import User, OauthAccount, CreateUser, CreateOauthAccount, PendingRegistration, CreatePendingRegistration
from services import user_services, auth_services
from config import oauth
import secrets

router = APIRouter(prefix="/api/auth")

@router.get("/login/{provider}")
async def login(request: Request, provider: str):
    oauth_client = oauth.create_client(provider)

    if oauth_client is None:
        raise HTTPException(
            status_code=404,
            detail="Oauth provider not supported"
        )

    redirect_uri = request.url_for(
        "auth_callback",
        provider=provider
    )

    # If the provider is Discord we need to set prompt to "none" so that a returning user isn't prompted
    if provider == "discord":
        return await oauth_client.authorize_redirect(request, redirect_uri, prompt="none")

    return await oauth_client.authorize_redirect(request, redirect_uri)

@router.post("/logout")
async def logout(request: Request):
    user_id = request.session.get("user_id")

    if not isinstance(user_id, int):
        raise HTTPException(
            status_code=401,
            detail="You have not logged in"
        )

    user = await user_services.get_user(user_id)

    # Handle if existing_user is None
    if user is None:
        request.session.pop("user_id", None)
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    await auth_services.record_logout(user)

    request.session.pop("user_id", None)

    return {"message": "You have been logged out"}

async def get_oauth_user_data(request: Request, provider: str) -> dict:
    oauth_client = oauth.create_client(provider)

    if oauth_client is None:
        raise HTTPException(
            status_code=404,
            detail="OAuth provider not supported"
        )

    token = await oauth_client.authorize_access_token(request)

    if provider == 'google':
        user_data = token['userinfo']

        return {
            'provider': 'google',
            'username': user_data['name'],
            'provider_id': user_data['sub'],
            'provider_email': user_data['email'],
        }
    elif provider == 'discord':
        response = await oauth_client.get(
            "users/@me",
            token=token
        )

        user_data = response.json()

        return {
            'provider': 'discord',
            'username': user_data['username'],
            'provider_id': user_data['id'],
            'provider_email': user_data['email'],
        }
    elif provider == 'github':
        response = await oauth_client.get("user", token=token)
        response.raise_for_status()
        user_data = response.json()

        email = user_data.get("email")

        if email is None:
            response = await oauth_client.get("user/emails", token=token)
            response.raise_for_status()

            emails = response.json()

            email = next(
                (
                    item["email"]
                    for item in emails
                    if item["primary"] and item["verified"]
                ),
                None
            )

        return {
            'provider': 'github',
            'username': user_data['login'],
            'provider_id': str(user_data['id']),
            'provider_email': email,    # <-- Emails for GitHub may be null if set to private
        }

    raise HTTPException(
        status_code=404,
        detail="Oauth provider not supported"
    )

async def validate_oauth_account(request: Request, oauth_data) -> User | PendingRegistration:
    current_user = await get_current_user(request)
    oauth_account = await auth_services.get_oauth_account(
        oauth_data['provider'],
        oauth_data['provider_id']
    )

    if isinstance(current_user, User):
        if isinstance(oauth_account, OauthAccount):
            # Verify the OAuth account belongs to the current user
            if oauth_account.user_id != current_user.id:
                raise HTTPException(
                    status_code=409,
                    detail="OAuth account already linked to another user"
                )

            return current_user

        else:
            # Link OAuth to the user
            await auth_services.link_oauth_account(
                current_user,
                CreateOauthAccount(
                    provider=oauth_data['provider'],
                    provider_id=oauth_data['provider_id'],
                    provider_email=oauth_data['provider_email'],
                )
            )

            return current_user

    elif isinstance(oauth_account, OauthAccount):
        # Logs in user
        user = await user_services.get_user(oauth_account.user_id)

        if not isinstance(user, User):
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return user

    # Check if any Users have a matching email
    if await auth_services.check_matching_email(oauth_data['provider_email']):
        token = secrets.token_urlsafe(32)

        create_pending = CreatePendingRegistration(
                username=oauth_data['username'],
                provider=oauth_data['provider'],
                provider_id=oauth_data['provider_id'],
                provider_email=oauth_data['provider_email']
            )

        pending_registration = await auth_services.create_pending_registration(token, create_pending)

        request.session["pending_registration"] = token

        return pending_registration

    # Logic for registering a new user
    new_user, _ = await auth_services.register_user(
        CreateUser(
            username=oauth_data['username']
        ),
        CreateOauthAccount(
            provider=oauth_data['provider'],
            provider_id=oauth_data['provider_id'],
            provider_email=oauth_data['provider_email']
        )
    )

    return new_user

async def get_current_user(request: Request) -> User | None:
    user_id = request.session.get("user_id")

    if isinstance(user_id, int):
        user = await user_services.get_user(user_id)

        if isinstance(user, User):
            return user

        request.session.pop("user_id", None)

    return None

@router.get("/callback/{provider}", name="auth_callback")
async def auth_callback(request: Request, provider: str):
    oauth_data = await get_oauth_user_data(request, provider)
    result = await validate_oauth_account(request, oauth_data)

    # If we find a matching email while registering a new user
    if isinstance(result, PendingRegistration):
        return RedirectResponse(url="/registration/confirm")

    # Save user id to session
    request.session['user_id'] = result.id

    await auth_services.record_login(result)

    return RedirectResponse(url="/gallery")

@router.post("/registration/confirm")
async def confirm_registration(request: Request):
    token = request.session.get("pending_registration")

    if not isinstance(token, str):
        raise HTTPException(
            status_code=404,
            detail="Pending registration not found"
        )

    pending = await auth_services.find_pending_registration(token)

    if not isinstance(pending, PendingRegistration):
        raise HTTPException(
            status_code=400,
            detail="Error finding pending registration session"
        )

    # Logic for registering a new user
    new_user, _ = await auth_services.register_user(
        CreateUser(
            username=pending.username
        ),
        CreateOauthAccount(
            provider=pending.provider,
            provider_id=pending.provider_id,
            provider_email=pending.provider_email
        )
    )

    request.session['user_id'] = new_user.id

    await auth_services.record_login(new_user)

    return RedirectResponse(
        url="/gallery",
        status_code=303
    )