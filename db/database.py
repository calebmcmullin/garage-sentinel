from db.connection import get_connection
from models import User, CreateUser, OauthAccount, CreateOauthAccount, CreateFile, File, PendingRegistration, CreatePendingRegistration
from pathlib import Path

schema_path = Path(__file__).parent / "schema.sql"

async def init_db():
    async with get_connection() as conn:
        await conn.executescript(schema_path.read_text())

async def get_user_by_id(user_id: int) -> User | None:
    async with get_connection() as conn:
        cursor = await conn.execute("""
            SELECT id, username, role
            FROM users
            WHERE id = ?
        """, (user_id,))
        row = await cursor.fetchone()

        if row is None:
            return None

        return User(
            id=row[0],
            username=row[1],
            role=row[2]
        )

async def get_user_id_by_provider_email(provider_email: str) -> int | None:
    async with get_connection() as conn:
        cursor = await conn.execute("""
            SELECT user_id
            FROM oauth_accounts
            WHERE LOWER(provider_email) = LOWER(?)
            LIMIT 1
        """, (provider_email,))

        row = await cursor.fetchone()

        if row is None:
            return None

        return row[0]

async def get_users() -> list[User]:
    async with get_connection() as conn:
        cursor = await conn.execute("""
            SELECT *
            FROM users
        """)
        rows = await cursor.fetchall()

        users = [
            User(
                id=row[0],
                username=row[1],
                role=row[2]
            )
            for row in rows
        ]
    return users

async def get_oauth_accounts() -> list[OauthAccount]:
    async with get_connection() as conn:
        cursor = await conn.execute("""
            SELECT *
            FROM oauth_accounts
        """)

        oauth_accounts = [
            OauthAccount(
                id=row[0],
                user_id=row[1],
                provider=row[2],
                provider_id=row[3],
                provider_email=row[4]
            ) for row in await cursor.fetchall()
        ]

        return oauth_accounts

async def create_user_with_oauth(create_user: CreateUser, create_oauth_account: CreateOauthAccount) -> tuple[User, OauthAccount]:
    async with get_connection() as conn:
        cursor = await conn.execute("""
            INSERT INTO users (username, role)
            VALUES (?, ?)
            RETURNING id, username, role
        """, (
            create_user.username,
            create_user.role
            )
        )

        user = User(
            id=cursor.lastrowid,
            username=create_user.username,
            role=create_user.role
        )

        cursor = await conn.execute("""
            INSERT INTO oauth_accounts (user_id, provider, provider_id, provider_email)
            VALUES (?, ?, ?, ?)
        """, (
            user.id,
            create_oauth_account.provider,
            create_oauth_account.provider_id,
            create_oauth_account.provider_email
            )
        )

        oauth_account = OauthAccount(
            id=cursor.lastrowid,
            user_id=user.id,
            provider=create_oauth_account.provider,
            provider_id=create_oauth_account.provider_id,
            provider_email=create_oauth_account.provider_email
        )

        await conn.commit()

        return user, oauth_account

async def link_oauth_account(user: User, create_oauth_account: CreateOauthAccount) -> OauthAccount:
    async with get_connection() as conn:
        cursor = await conn.execute("""
            INSERT INTO oauth_accounts(user_id, provider, provider_id, provider_email)
            VALUES (?, ?, ?, ?)
        """, (
            user.id,
            create_oauth_account.provider,
            create_oauth_account.provider_id,
            create_oauth_account.provider_email
            )
        )

        await conn.commit()

        return OauthAccount(
            id=cursor.lastrowid,
            user_id=user.id,
            provider=create_oauth_account.provider,
            provider_id=create_oauth_account.provider_id,
            provider_email=create_oauth_account.provider_email
        )

async def get_oauth_account(provider: str, provider_id: str) -> OauthAccount | None:
    async with get_connection() as conn:
        cursor = await conn.execute("""
            SELECT *
            FROM oauth_accounts
            WHERE provider = ? AND provider_id = ?
        """, (provider, provider_id,))

        row = await cursor.fetchone()

        if row is None:
            return None

        return OauthAccount(
            id=row[0],
            user_id=row[1],
            provider=row[2],
            provider_id=row[3],
            provider_email=row[4],
        )

async def get_oauth_accounts_by_user_id(user_id: int) -> list[OauthAccount]:
    async with get_connection() as conn:
        cursor = await conn.execute("""
            SELECT *
            FROM oauth_accounts
            WHERE user_id = ?
        """, (user_id,))

        oauth_accounts = [
            OauthAccount(
                id=row[0],
                user_id=row[1],
                provider=row[2],
                provider_id=row[3],
                provider_email=row[4]
            ) for row in await cursor.fetchall()
        ]

        return oauth_accounts

async def update_username(user_id: int, username: str) -> bool:
    async with get_connection() as conn:
        cursor = await conn.execute("""
            UPDATE users
            SET username = ?
            WHERE id = ?;
        """, (username, user_id))

        await conn.commit()

        return cursor.rowcount > 0

async def delete_user(user_id: int) -> bool:
    async with get_connection() as conn:
        cursor = await conn.execute("""
            DELETE FROM users WHERE id = ?
        """, (user_id,))

        await conn.commit()

        return cursor.rowcount > 0

async def add_file(create_file: CreateFile) -> File:
    async with get_connection() as conn:
        cursor = await conn.execute("""
            INSERT INTO files (user_id, filename, filetype, storage_name)
            VALUES (?, ?, ?, ?)
            RETURNING *
        """, (create_file.user_id, create_file.filename, create_file.filetype, create_file.storage_name)
        )

        rows = await cursor.fetchone()

        await conn.commit()

        return File(
            id=cursor.lastrowid,
            user_id=rows[1],
            filename=rows[2],
            filetype=rows[3],
            storage_name=rows[4],
            created_at=rows[5],
        )

async def get_files_by_user_id(user_id: int, filetypes: list[str] | None = None) -> list[File]:
    async with get_connection() as conn:
        query = "SELECT * FROM files"
        params = []

        query += " WHERE user_id = ?"
        params.append(user_id)

        if filetypes:
            placeholders = ",".join("?" for _ in filetypes)
            query += f" AND filetype IN ({placeholders})"
            params.extend(filetypes)

        cursor = await conn.execute(query, params)

        files = [
            File(
                id=row[0],
                user_id=row[1],
                filename=row[2],
                filetype=row[3],
                storage_name=row[4],
                created_at=row[5],
            )
            for row in await cursor.fetchall()
        ]

        return files

async def get_file_by_storage_name(storage_name: str) -> File:
    async with get_connection() as conn:
        cursor = await conn.execute("""
            SELECT *
            FROM files
            WHERE storage_name = ?
        """, (storage_name,)
        )

        row = await cursor.fetchone()

        return File(
            id=row[0],
            user_id=row[1],
            filename=row[2],
            filetype=row[3],
            storage_name=row[4],
            created_at=row[5],
        )

async def log_activity(user_id: int, action: str, details: str) -> bool:
    async with get_connection() as conn:
        cursor = await conn.execute("""
        INSERT INTO activity_log(user_id, action, details)
        VALUES (?, ?, ?)
        """, (user_id, action, details))

        await conn.commit()

        return cursor.rowcount > 0

async def create_pending_registration(token_hash: str, create_pending: CreatePendingRegistration) -> PendingRegistration:
    async with get_connection() as conn:
        await conn.execute("""
            INSERT INTO pending_registrations (token_hash, username, provider, provider_id, provider_email)
            VALUES (?, ?, ?, ?, ?)
        """, (
            token_hash,
            create_pending.username,
            create_pending.provider,
            create_pending.provider_id,
            create_pending.provider_email
            )
        )

        await conn.commit()

        return PendingRegistration(
            token_hash=token_hash,
            username=create_pending.username,
            provider=create_pending.provider,
            provider_id=create_pending.provider_id,
            provider_email=create_pending.provider_email
        )

async def delete_pending_registration(token_hash: str) -> bool:
    async with get_connection() as conn:
        await conn.execute("""
        DELETE FROM pending_registrations
        WHERE token_hash = ?
        """, (token_hash,)
        )

        await conn.commit()

        return True

async def find_pending_registration(token_hash: str) -> PendingRegistration | None:
    async with get_connection() as conn:
        cursor = await conn.execute("""
            SELECT *
            FROM pending_registrations
            WHERE token_hash = ?
        """, (token_hash,))

        row = await cursor.fetchone()

        if row is None:
            return None

        return PendingRegistration(
            token_hash=row[0],
            username=row[1],
            provider=row[2],
            provider_id=row[3],
            provider_email=row[4]
        )

async def delete_expired_registrations(expiration_minutes: int):
    async with get_connection() as conn:
        await conn.execute("""
            DELETE FROM pending_registrations
            WHERE created_at <= datetime('now', ?)
        """, (f"-{expiration_minutes} minutes",))

        await conn.commit()