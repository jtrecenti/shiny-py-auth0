# shiny-auth0

Autenticação fácil para Shiny Python apps usando [Auth0](https://auth0.com/).

## Instalação

```bash
pip install git+https://github.com/jtrecenti/shiny-py-auth0.git
```

## Como funciona

- Você cria/configura seu app no Auth0 e salva as credenciais em um arquivo `_auth0.yml` ou via variáveis de ambiente.
- Use o wrapper `AppAuth0()` para proteger seu app.
- O pacote cuida do login/logout, validação do token e disponibiliza as informações do usuário na sessão (`session.user`).

## Exemplo rápido

Veja exemplos completos em `examples/`.

```python
from shiny import render, reactive, ui
from shiny_auth0.auth import AppAuth0, send_auth0_logout

app_ui = ui.page_fluid(
    ui.h2("Exemplo: Login, Logout e Proteção de Rotas"),
    ui.output_text("user_email"),
    ui.output_text("login_status"),
    ui.input_action_button("logout", "Logout")
)

def server(input, output, session):
    @render.text
    def user_email():
        user_info = session.user
        if user_info:
            return f"Email: {user_info.get('email', 'Desconhecido')}"
        else:
            return "Não autenticado."

    @render.text
    def login_status():
        user_info = session.user
        return "Logado!" if user_info else "Faça login para continuar."

    @reactive.effect
    @reactive.event(input.logout)
    async def logout():
        await send_auth0_logout(session)

app = AppAuth0(app_ui, server)
```

> **Nota:** O handler JavaScript para logout já é incluído automaticamente pelo `AppAuth0`.

## Configuração (_auth0.yml ou .env)

Crie um arquivo `examples/_auth0.yml`:

```yaml
auth0:
  domain: "YOUR_DOMAIN.auth0.com"
  client_id: "YOUR_CLIENT_ID"
  client_secret: "YOUR_CLIENT_SECRET"
  redirect_uri: "http://localhost:8000"
  audience: "YOUR_API_IDENTIFIER"  # (opcional)
```

Ou configure via variáveis de ambiente (veja `.env.example`).

- `AUTH0_DOMAIN`
- `AUTH0_CLIENT_ID`
- `AUTH0_CLIENT_SECRET`
- `AUTH0_REDIRECT_URI`
- `AUTH0_AUDIENCE` (opcional)

---
Inspirado em [curso-r/auth0](https://github.com/curso-r/auth0).
