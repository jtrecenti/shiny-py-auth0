from shiny import ui, render, reactive
from shiny_auth0 import AppAuth0, send_auth0_logout

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
        if user_info:
            return "Logado!"
        else:
            return "Faça login para continuar."

    @reactive.effect
    @reactive.event(input.logout)
    async def logout():
        # Redireciona para logout do Auth0
        await send_auth0_logout(session)

app = AppAuth0(app_ui, server)
