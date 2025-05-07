from shiny_auth0.auth import AppAuth0, get_user_info
from shiny import ui, render
from starlette.requests import Request

# UI protegida
def app_ui(request: Request):
    return ui.page_fluid(
        ui.h2("Exemplo protegido com Auth0!"),
        ui.output_text("user_email")
    )

# Server protegido
def server(input, output, session):
    @output()
    @render.text
    def user_email():
        user_info = session.user
        return user_info.get("email", "Desconhecido")

# Criação do app usando AppAuth0 (state compartilhado)
app = AppAuth0(app_ui, server)
