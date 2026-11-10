from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
import os

load_dotenv()

SESSION_SECRET=os.getenv("SESSION_SECRET")

# GOOGLE
GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET")

# DISCORD
DISCORD_CLIENT_ID=os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET=os.getenv("DISCORD_CLIENT_SECRET")

# GITHUB
GITHUB_CLIENT_ID=os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET=os.getenv("GITHUB_CLIENT_SECRET")

if SESSION_SECRET is None:
    raise RuntimeError("SESSION_SECRET not set")

if GOOGLE_CLIENT_ID is None:
    raise RuntimeError("GOOGLE_CLIENT_ID not set")
if GOOGLE_CLIENT_SECRET is None:
    raise RuntimeError("GOOGLE_CLIENT_SECRET not set")

if DISCORD_CLIENT_ID is None:
    raise RuntimeError("DISCORD_CLIENT_ID not set")
if DISCORD_CLIENT_SECRET is None:
    raise RuntimeError("DISCORD_CLIENT_SECRET not set")

if GITHUB_CLIENT_ID is None:
    raise RuntimeError("GITHUB_CLIENT_ID not set")
if GITHUB_CLIENT_SECRET is None:
    raise RuntimeError("GITHUB_CLIENT_SECRET not set")

# Register Oauth
oauth = OAuth()

oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    }
)
oauth.register(
    name="discord",
    client_id=DISCORD_CLIENT_ID,
    client_secret=DISCORD_CLIENT_SECRET,
    authorize_url="https://discord.com/oauth2/authorize",
    access_token_url="https://discord.com/api/oauth2/token",
    api_base_url="https://discord.com/api/",
    client_kwargs={
        "scope": "identify email"
    }
)
oauth.register(
    name="github",
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    authorize_url="https://github.com/login/oauth/authorize",
    access_token_url="https://github.com/login/oauth/access_token",
    api_base_url="https://api.github.com/",
    client_kwargs={
        "scope": "read:user user:email"
    }
)