from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools._common import client_from
from utils.webcite_api import WebciteError


class WebciteProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """Checks the key with the free credit balance call; no credits are spent."""
        try:
            client = client_from(credentials)
            try:
                client.balance()
            finally:
                client.close()
        except WebciteError as e:
            raise ToolProviderCredentialValidationError(str(e)) from e
