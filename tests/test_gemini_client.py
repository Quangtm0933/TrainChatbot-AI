"""Property-based tests for utils/gemini_client.py."""

import os
import tempfile
from unittest.mock import MagicMock, patch

from hypothesis import given, settings
from hypothesis import strategies as st

from utils.gemini_client import load_api_key, send_message

# ASCII whitespace characters that dotenv can reliably parse
ASCII_WHITESPACE = " \t\n\r\x0b\x0c"


class TestLoadApiKeyWhitespaceRejection:
    """Property 1: Empty and whitespace-only API keys are rejected.

    For any string composed entirely of whitespace characters (including the
    empty string), load_api_key() SHALL treat it as missing and return None.

    **Validates: Requirements 2.3**
    """

    @given(
        whitespace_key=st.text(
            alphabet=ASCII_WHITESPACE,
            min_size=0,
            max_size=20,
        )
    )
    @settings(max_examples=100)
    def test_whitespace_only_keys_are_rejected(self, whitespace_key: str):
        """load_api_key returns None for any whitespace-only API key."""
        original_dir = os.getcwd()
        tmp_dir = tempfile.mkdtemp()
        try:
            os.chdir(tmp_dir)

            # Write .env with UTF-8 encoding explicitly
            env_path = os.path.join(tmp_dir, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(f"GEMINI_API_KEY={whitespace_key}\n")

            # Clean env var to avoid leakage from prior runs
            os.environ.pop("GEMINI_API_KEY", None)

            result = load_api_key()

            assert result is None, (
                f"Expected None for whitespace-only key "
                f"{whitespace_key!r}, got {result!r}"
            )
        finally:
            os.chdir(original_dir)
            os.environ.pop("GEMINI_API_KEY", None)


# Strategy: generate a chat history as a list of dicts with role in
# ["user", "assistant"] and arbitrary text content.
chat_history_strategy = st.lists(
    st.fixed_dictionaries(
        {
            "role": st.sampled_from(["user", "assistant"]),
            "content": st.text(min_size=0, max_size=50),
        }
    ),
    min_size=0,
    max_size=20,
)


class TestHistoryToContentsConversion:
    """Property 2: History-to-contents conversion preserves all messages in order.

    For any chat history (list of {"role", "content"} dicts) and any user prompt
    string, the contents list built by send_message SHALL contain all history
    messages in their original order followed by the current prompt, with correct
    role mapping ("assistant" → "model").

    **Validates: Requirements 4.1**
    """

    @given(
        history=chat_history_strategy,
        prompt=st.text(min_size=1, max_size=50),
    )
    @settings(max_examples=100)
    @patch("utils.gemini_client.genai.Client")
    def test_history_to_contents_preserves_order_and_roles(
        self, mock_client_cls: MagicMock, history: list[dict], prompt: str
    ):
        """send_message builds contents with all history messages in order,
        correct role mapping, and the current prompt appended last."""
        # Set up mock so no real API call is made
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "mock response"
        mock_client.models.generate_content.return_value = mock_response

        # Call the function under test
        send_message(api_key="fake-key", prompt=prompt, history=history)

        # Capture the contents argument passed to generate_content
        call_args = mock_client.models.generate_content.call_args
        contents = call_args.kwargs.get("contents") or call_args[1].get("contents")
        if contents is None:
            # Try positional args — contents is the second arg after model
            contents = call_args[0][1] if len(call_args[0]) > 1 else call_args.kwargs["contents"]

        # Verify length: history messages + 1 for the current prompt
        assert len(contents) == len(history) + 1, (
            f"Expected {len(history) + 1} content entries, got {len(contents)}"
        )

        # Verify each history message appears in order with correct role mapping
        for i, msg in enumerate(history):
            expected_role = "model" if msg["role"] == "assistant" else msg["role"]
            assert contents[i].role == expected_role, (
                f"Entry {i}: expected role {expected_role!r}, "
                f"got {contents[i].role!r}"
            )
            assert contents[i].parts[0].text == msg["content"], (
                f"Entry {i}: expected content {msg['content']!r}, "
                f"got {contents[i].parts[0].text!r}"
            )

        # Verify the last entry is the current prompt with role "user"
        last = contents[-1]
        assert last.role == "user", (
            f"Last entry role: expected 'user', got {last.role!r}"
        )
        assert last.parts[0].text == prompt, (
            f"Last entry content: expected {prompt!r}, got {last.parts[0].text!r}"
        )


class TestApiResponsePassthrough:
    """Property 3: API response text passthrough.

    For any successful Gemini API response, send_message SHALL return the
    response text exactly as received, without modification.

    **Validates: Requirements 4.2**
    """

    @given(
        response_text=st.text(min_size=1, max_size=200),
    )
    @settings(max_examples=100)
    @patch("utils.gemini_client.genai.Client")
    def test_send_message_returns_response_text_exactly(
        self, mock_client_cls: MagicMock, response_text: str
    ):
        """send_message returns the API response text without modification."""
        # Set up mock so no real API call is made
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = response_text
        mock_client.models.generate_content.return_value = mock_response

        # Call the function under test
        result = send_message(api_key="fake-key", prompt="test", history=[])

        # The returned value must be exactly the response text
        assert result == response_text, (
            f"Expected {response_text!r}, got {result!r}"
        )


# ---------------------------------------------------------------------------
# Unit tests for load_api_key and send_message
# Requirements: 2.1, 2.2, 2.3, 4.1, 4.2, 4.3
# ---------------------------------------------------------------------------


class TestLoadApiKeyUnit:
    """Unit tests for load_api_key covering valid .env, missing .env,
    empty key, and unset key scenarios."""

    def test_valid_env_returns_key(self, tmp_path, monkeypatch):
        """load_api_key returns the key string when .env has a valid key."""
        env_file = tmp_path / ".env"
        env_file.write_text("GEMINI_API_KEY=test-api-key-123\n")
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)

        result = load_api_key()

        assert result == "test-api-key-123"

    def test_missing_env_returns_none(self, tmp_path, monkeypatch):
        """load_api_key returns None when .env file does not exist."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)

        result = load_api_key()

        assert result is None

    def test_empty_key_returns_none(self, tmp_path, monkeypatch):
        """load_api_key returns None when GEMINI_API_KEY is set but empty."""
        env_file = tmp_path / ".env"
        env_file.write_text("GEMINI_API_KEY=\n")
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)

        result = load_api_key()

        assert result is None

    def test_key_not_set_returns_none(self, tmp_path, monkeypatch):
        """load_api_key returns None when .env exists but GEMINI_API_KEY is absent."""
        env_file = tmp_path / ".env"
        env_file.write_text("OTHER_VAR=hello\n")
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)

        result = load_api_key()

        assert result is None


class TestSendMessageUnit:
    """Unit tests for send_message covering response extraction,
    error propagation, and history role conversion."""

    @patch("utils.gemini_client.genai.Client")
    def test_response_text_extracted(self, mock_client_cls):
        """send_message returns the response text from the API."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "Hello from Gemini!"
        mock_client.models.generate_content.return_value = mock_response

        result = send_message(api_key="key", prompt="Hi", history=[])

        assert result == "Hello from Gemini!"

    @patch("utils.gemini_client.genai.Client")
    def test_api_error_propagates(self, mock_client_cls):
        """send_message lets API exceptions propagate to the caller."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.models.generate_content.side_effect = RuntimeError("API down")

        import pytest as _pytest

        with _pytest.raises(RuntimeError, match="API down"):
            send_message(api_key="key", prompt="Hi", history=[])

    @patch("utils.gemini_client.genai.Client")
    def test_assistant_role_mapped_to_model(self, mock_client_cls):
        """send_message maps 'assistant' role to 'model' in contents."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "ok"
        mock_client.models.generate_content.return_value = mock_response

        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]
        send_message(api_key="key", prompt="How are you?", history=history)

        call_args = mock_client.models.generate_content.call_args
        contents = call_args.kwargs.get("contents") or call_args[1].get("contents")
        if contents is None:
            contents = call_args[0][1]

        # history[0] — user stays "user"
        assert contents[0].role == "user"
        # history[1] — assistant becomes "model"
        assert contents[1].role == "model"
        # last entry — current prompt is "user"
        assert contents[2].role == "user"
        assert contents[2].parts[0].text == "How are you?"
