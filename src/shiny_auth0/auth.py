import os
import yaml
from functools import wraps
from shiny import Session
from .utils import load_auth0_config, validate_jwt, get_auth0_client
from .exceptions import Auth0Error
from starlette.requests import Request

from functools import wraps
from shiny import Session
from .utils import load_auth0_config, validate_jwt
from .exceptions import Auth0Error

def auth0_ui(app_ui_func=None, config_path=None, state=None):
    """
    Decorator to protect Shiny for Python app_ui with Auth0 authentication.
    If user is not authenticated, redirects to Auth0 login.
    Handles Auth0 callback with ?code=... in URL.
    Recebe o parâmetro state para proteção CSRF.
    """
    from shiny import ui
    import urllib.parse
    import logging
    logger = logging.getLogger("shiny_auth0")
    logging.basicConfig(level=logging.INFO)
    def decorator(func):
        @wraps(func)
        def wrapper(request: Request, *args, **kwargs):
            config = load_auth0_config(config_path)
            code = request.query_params.get("code")
            state_param = request.query_params.get("state")
            if code:
                logger.info(f"Recebido code na URL: {code}. Apenas validando state e repassando para o server...")
                # Validação do state (proteção CSRF)
                if state_param and state:
                    if state_param != state:
                        logger.warning(f"State inválido! Recebido: {state_param}, esperado: {state}")
                        return ui.tags.h3("Erro de autenticação: state inválido (possível CSRF).")
                    else:
                        logger.info(f"State validado com sucesso: {state_param}")
                elif state_param:
                    logger.warning("State recebido mas não havia state esperado.")
                else:
                    logger.info("Nenhum parâmetro state recebido na URL.")
                # Apenas renderiza a UI normalmente, sem tentar autenticar ou acessar session
                return func(request, *args, **kwargs)
            # Se não autenticado nem com code, redireciona para Auth0 login
            # TODO: é necessário ter isso?
            if state is None:
                import secrets
                state_val = secrets.token_urlsafe(16)
            else:
                state_val = state
            params = {
                "client_id": config["client_id"],
                "response_type": "code",
                "redirect_uri": config["redirect_uri"],
                "scope": "openid profile email",
                "state": state_val
            }
            login_url = f"https://{config['domain']}/authorize?" + urllib.parse.urlencode(params)
            logger.info(f"Usando state para CSRF: {state_val}")
            logger.info(f"Redirecionando para Auth0 login: {login_url}")
            return ui.tags.script(f"window.location.replace('{login_url}');")
        return wrapper
    if app_ui_func is not None:
        return decorator(app_ui_func)
    return decorator


def auth0_server(server_func=None, config_path=None, state=None):
    """
    Decorator/factory to protect a Shiny for Python server with Auth0 authentication.
    Passes user_info as an extra argument to the server function.
    Set AUTH0_DISABLE=1 in your environment or config to disable authentication (for development).
    Agora aceita o argumento opcional state para compatibilidade com AppAuth0 e padrão R.
    """
    import logging
    logger = logging.getLogger("shiny_auth0")
    logging.basicConfig(level=logging.INFO)
    def decorator(func):
        @wraps(func)
        def wrapper(input, output, session: Session, *args, **kwargs):
            disable = os.environ.get("AUTH0_DISABLE", "0") == "1"
            from shiny import reactive
            if disable:
                logger.info("[auth0_server] Autenticação desabilitada (AUTH0_DISABLE=1). user_info será vazio.")
                def user_info():
                    return {}
            else:
                @reactive.calc
                def user_info():
                    if getattr(session, "user", None):
                        logger.info("[auth0_server] Usuário já autenticado na sessão.")
                        return session.user
                    logger.info("[auth0_server] Tentando autenticar usuário a partir do token/code da requisição.")
                    config = load_auth0_config(config_path)
                    from urllib.parse import parse_qs
                    params_str = session.clientdata.url_search()
                    if params_str.startswith("?"):
                        params_str = params_str[1:]
                    params = parse_qs(params_str)
                    code = params.get("code", [None])[0]
                    state = params.get("state", [None])[0]
                    if not code:
                        raise Auth0Error("Código de autorização (code) não encontrado na URL.")
                    info = validate_jwt(code, config, state=state)
                    logger.info(f"[auth0_server] JWT válido. user_info extraído: {info}")
                    return info
            @reactive.effect
            def _():
                session.user = user_info()
            return func(input, output, session, *args, **kwargs)
        return wrapper
    if server_func is not None:
        return decorator(server_func)
    return decorator

def get_user_info(session: Session):
    """Retrieve authenticated user info from the session."""
    return session.user()

def AppAuth0(app_ui, server, config_path=None, static_assets=None, debug=False):
    """
    Função para criar App Shiny Python com Auth0, gerando state único e passando para UI e server.
    Aceita os mesmos parâmetros que shiny.App para máxima compatibilidade.
    """
    import secrets
    from shiny import App
    from htmltools import TagList
    state = secrets.token_urlsafe(16)

    def app_ui_func(request: Request):
        return TagList(app_ui, auth0_logout_js())

    return App(
        auth0_ui(app_ui_func, config_path=config_path, state=state),
        auth0_server(server, config_path=config_path, state=state),
        static_assets=static_assets,
        debug=debug
    )

def auth0_logout_js():
    """
    Retorna um bloco ui.tags.script com o handler JS para custom message de logout do Auth0.
    Inclua esse bloco no seu app_ui.
    """
    from shiny import ui
    return ui.tags.script(
        '''
        $(function() {
            Shiny.addCustomMessageHandler("auth0_redirect", function(message) {
                window.location.replace(message.url);
            });
        });
        '''
    )

async def send_auth0_logout(session, config_path="examples/_auth0.yml"):
    """
    Envia a mensagem customizada para redirecionar o usuário para o logout do Auth0.
    """
    from .utils import load_auth0_config
    import urllib.parse
    config = load_auth0_config(config_path)
    domain = config["domain"]
    client_id = config["client_id"]
    redirect_uri = config["redirect_uri"]
    return_to = urllib.parse.quote(redirect_uri, safe="")
    logout_url = f"https://{domain}/v2/logout?client_id={client_id}&returnTo={return_to}"
    await session.send_custom_message("auth0_redirect", {"url": logout_url})

