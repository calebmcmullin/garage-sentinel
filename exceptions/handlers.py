from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import html

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return HTMLResponse(
        content=f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="color-scheme" content="dark">
            <title>Error {exc.status_code} | Garage Sentinel</title>
            <style>
                * {{ box-sizing: border-box; margin: 0; padding: 0; }}

                :root {{
                    --bg: #0b0f14;
                    --panel: #111821;
                    --panel-soft: #151e28;
                    --border: #233041;
                    --text: #edf3f8;
                    --muted: #8fa0b3;
                    --accent: #7dd3fc;
                    --accent-soft: rgba(125, 211, 252, 0.12);
                }}

                body {{
                    min-height: 100vh;
                    font-family: Inter, ui-sans-serif, system-ui,
                                 -apple-system, BlinkMacSystemFont,
                                 "Segoe UI", sans-serif;
                    background: radial-gradient(circle at top,
                        rgba(37, 99, 235, .08), transparent 45%), var(--bg);
                    color: var(--text);
                    line-height: 1.6;
                }}

                header {{
                    padding: 22px max(24px, calc((100vw - 1120px) / 2));
                    border-bottom: 1px solid var(--border);
                    background: rgba(11, 15, 20, .88);
                }}

                .brand {{ display: flex; align-items: center; gap: 12px; }}

                .logo {{
                    width: 40px;
                    height: 40px;
                    display: grid;
                    place-items: center;
                    background: var(--accent-soft);
                    border: 1px solid rgba(125, 211, 252, .22);
                    border-radius: 11px;
                    font-size: 20px;
                }}

                .brand strong {{ font-size: 15px; }}
                .brand span {{ display: block; font-size: 12px; color: var(--muted); }}

                main {{
                    min-height: calc(100vh - 250px);
                    display: grid;
                    place-items: center;
                    padding: 60px 20px;
                }}

                .content {{ width: 100%; max-width: 430px; text-align: center; }}

                .eyebrow {{
                    color: var(--accent);
                    font-size: 12px;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: .13em;
                    margin-bottom: 12px;
                }}

                h1 {{
                    font-size: clamp(34px, 5vw, 44px);
                    line-height: 1.1;
                    letter-spacing: -.04em;
                }}

                .subtitle {{ margin: 13px 0 28px; font-size: 15px; color: var(--muted); }}

                .panel {{
                    border: 1px solid var(--border);
                    border-radius: 16px;
                    background: linear-gradient(180deg,
                        rgba(17, 24, 33, .96), rgba(13, 19, 26, .96));
                    padding: 30px;
                }}

                .panel h2 {{ font-size: 18px; margin-bottom: 8px; }}
                .panel p {{ color: var(--muted); font-size: 13px; margin-bottom: 24px; }}

                .home-button {{
                    display: block;
                    padding: 14px 18px;
                    border: 1px solid var(--border);
                    border-radius: 10px;
                    background: var(--panel-soft);
                    color: var(--text);
                    text-decoration: none;
                    font-size: 15px;
                    font-weight: 600;
                    transition: .2s;
                }}

                .home-button:hover {{
                    background: var(--accent-soft);
                    border-color: var(--accent);
                    transform: translateY(-2px);
                }}

                .footer-note {{
                    color: var(--muted);
                    font-size: 12px;
                    margin-top: 22px;
                }}
            </style>
        </head>
        <body>
            <header>
                <div class="brand">
                    <div class="logo">🛠️</div>
                    <div>
                        <strong>Garage Sentinel</strong>
                        <span>Your garage, connected.</span>
                    </div>
                </div>
            </header>

            <main>
                <div class="content">
                    <div class="eyebrow">Error {exc.status_code}</div>
                    <h1>Something went wrong.</h1>
                    <p class="subtitle">Looks like we've hit a bump in the road.</p>

                    <div class="panel">
                        <h2>Unable to complete request</h2>
                        <p>{html.escape(str(exc.detail))}</p>
                        <a class="home-button" href="/">Return to Home →</a>
                    </div>

                    <div class="footer-note">
                        Garage Sentinel · Error {exc.status_code}
                    </div>
                </div>
            </main>
        </body>
        </html>
        """,
        status_code=exc.status_code
    )
