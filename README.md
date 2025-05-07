# shiny-auth0

Autenticação fácil para Shiny Python apps usando [Auth0](https://auth0.com/).

## Instalação

```bash
pip install .
```

## Como funciona

- Você cria/configura seu app no Auth0 e salva as credenciais em um arquivo `_auth0.yml` ou via variáveis de ambiente.
- Use o wrapper `with_auth0()` para proteger seu app.
- O pacote cuida do login/logout, validação do token e disponibiliza as informações do usuário na sessão.

## Exemplo rápido

Veja exemplos completos em `examples/`.

```python
from shiny import App, ui, render, output
from shiny_auth0 import with_auth0

app = App(
    ui.page_fluid(
        ui.h2("Exemplo protegido com Auth0!"),
        ui.output_text("user_email")
    ),
    server=with_auth0(lambda input, output, session, user_info: (
        @output()
        @render.text
        def user_email():
            return user_info.get("email", "Desconhecido")
    ))
)
```

## Configuração (_auth0.yml)

```yaml
name: myApp
auth0:
  domain: "YOUR_DOMAIN.auth0.com"
  client_id: "YOUR_CLIENT_ID"
  client_secret: "YOUR_CLIENT_SECRET"
  redirect_uri: "http://localhost:8000/auth0/callback"
  audience: "YOUR_API_IDENTIFIER"
```

Ou use variáveis de ambiente equivalentes.

---
Inspirado em [curso-r/auth0](https://github.com/curso-r/auth0).
