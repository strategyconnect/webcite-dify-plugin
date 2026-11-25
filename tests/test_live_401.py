"""Opt-in check of the live call path with a placeholder key. Spends no credits.

Run with: WEBCITE_LIVE_401=1 pytest tests/test_live_401.py
"""

from __future__ import annotations

import os

import pytest
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from provider.webcite import WebciteProvider


@pytest.mark.skipif(not os.environ.get("WEBCITE_LIVE_401"), reason="set WEBCITE_LIVE_401=1")
def test_placeholder_key_is_rejected_by_the_live_api() -> None:
    with pytest.raises(ToolProviderCredentialValidationError, match="HTTP 401"):
        WebciteProvider().validate_credentials({"webcite_api_key": "placeholder-not-a-key"})
