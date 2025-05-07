# shiny-auth0

Easy authentication for Shiny Python apps using [Auth0](https://auth0.com/).

## Installation

```bash
pip install git+https://github.com/jtrecenti/shiny-py-auth0.git
```

## Development Status

This package is in early development and may contain bugs. If you find any, please open an issue on the [repository](https://github.com/jtrecenti/shiny-py-auth0).

## How it works

- You create/configure your app in Auth0 and save the credentials in a `_auth0.yml` file or using environment variables.
- Use the `AppAuth0()` wrapper to protect your app. Importe diretamente de `shiny_auth0`:
- The package handles login/logout, token validation, and provides user information in the session (`session.user`).

## Quick Example

Veja exemplos completos na pasta `examples/` e use sempre:

```python
from shiny_auth0 import AppAuth0, send_auth0_logout
```


```python
from shiny import render, reactive, ui
from shiny_auth0 import AppAuth0, send_auth0_logout

app_ui = ui.page_fluid(
    ui.h2("Example: Login, Logout and Route Protection"),
    ui.output_text("user_email"),
    ui.output_text("login_status"),
    ui.input_action_button("logout", "Logout")
)

def server(input, output, session):
    @render.text
    def user_email():
        user_info = session.user
        if user_info:
            return f"Email: {user_info.get('email', 'Unknown')}"
        else:
            return "Not authenticated."

    @render.text
    def login_status():
        user_info = session.user
        return "Logged in!" if user_info else "Please log in to continue."

    @reactive.effect
    @reactive.event(input.logout)
    async def logout():
        await send_auth0_logout(session)

app = AppAuth0(app_ui, server)
```

> **Note:** The JavaScript handler for logout is included automatically by `AppAuth0`.

## Configuration (`_auth0.yml` or `.env`)

Create a file `examples/_auth0.yml`:

```yaml
auth0:
  domain: "YOUR_DOMAIN.auth0.com"
  client_id: "YOUR_CLIENT_ID"
  client_secret: "YOUR_CLIENT_SECRET"
  redirect_uri: "http://localhost:8000"
  audience: "YOUR_API_IDENTIFIER"  # (optional)
```

Or configure via environment variables (see `.env.example`):

- `AUTH0_DOMAIN`
- `AUTH0_CLIENT_ID`
- `AUTH0_CLIENT_SECRET`
- `AUTH0_REDIRECT_URI`
- `AUTH0_AUDIENCE` (optional)

---
Inspired by [curso-r/auth0](https://github.com/curso-r/auth0).
