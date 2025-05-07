from shiny_auth0 import AppAuth0
from shiny import ui, render

# UI protegida
app_ui = ui.page_fluid(
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
