##login

from authlib.integrations.flask_client import OAuth

from website.config import c

oauth = OAuth()
oauth.register(
    name='azure',
    client_id=c.OAUTH_AZURE_APP,
    client_secret=c.OAUTH_AZURE_KEY,
    access_token_url=c.OAUTH_AZURE_TOKEN_URL,
    access_token_params=None,
    authorize_url=c.OAUTH_AZURE_AUTH_URL,
    authorize_params=None,
    api_base_url=c.OAUTH_AZURE_BASE_URL,
    client_kwargs={'scope': c.OAUTH_AZURE_SCOPE},
)