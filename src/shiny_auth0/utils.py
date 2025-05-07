import os
import yaml
from auth0.authentication import GetToken
from jose import jwt
from .exceptions import Auth0Error
import requests

def load_auth0_config(config_path=None):
    """Carrega configurações do Auth0 de arquivo YAML ou variáveis de ambiente."""
    config = {}
    if config_path and os.path.exists(config_path):
        with open(config_path, "r") as f:
            yml = yaml.safe_load(f)
            config = yml.get("auth0", {})
    else:
        config = {
            "domain": os.getenv("AUTH0_DOMAIN"),
            "client_id": os.getenv("AUTH0_CLIENT_ID"),
            "client_secret": os.getenv("AUTH0_CLIENT_SECRET"),
            "redirect_uri": os.getenv("AUTH0_REDIRECT_URI"),
            "audience": os.getenv("AUTH0_AUDIENCE"),
        }
    if not config.get("domain"):
        raise Auth0Error("Auth0 domain não configurado!")
    return config

def get_auth0_client(config):
    return GetToken(config["domain"], config["client_id"], client_secret=config["client_secret"])

def fetch_userinfo(domain, access_token):
    """Busca informações do usuário autenticado no endpoint /userinfo do Auth0."""
    url = f"https://{domain}/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def validate_jwt(code, config, state=None):
    """Troca o code por access_token e retorna user_info do Auth0. 'state' é opcional para checagem de CSRF."""
    # Troca o code por access_token
    token_url = f"https://{config['domain']}/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "code": code,
        "redirect_uri": config["redirect_uri"],
        # "audience": config.get("audience"),  # Inclua se necessário
    }
    if config.get("audience"):
        payload["audience"] = config["audience"]
    resp = requests.post(token_url, json=payload)
    if not resp.ok:
        raise Auth0Error(f"Erro ao trocar code por token: {resp.text}")
    token_data = resp.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise Auth0Error("Access token não retornado pelo Auth0!")
    # Busca informações do usuário
    user_info = fetch_userinfo(config["domain"], access_token)
    return user_info
