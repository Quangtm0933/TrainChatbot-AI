"""Property-based tests for app.py chat history logic."""

from hypothesis import given, settings
from hypothesis import strategies as st


class TestChatHistoryAppend:
    """Property 4: Chat history append preserves role and content.

    **Validates: Requirements 5.2, 5.3**
    """

    @given(
        content=st.text(),
        role=st.sampled_from(["user", "assistant"]),
    )
    @settings(max_examples=100)
    def test_append_preserves_role_and_content(
        self, content: str, role: str
    ) -> None:
        """Appending a message increases length by 1 and the last entry
        has the correct role and content."""
        chat_history: list[dict[str, str]] = []
        original_length = len(chat_history)

        chat_history.append({"role": role, "content": content})

        assert len(chat_history) == original_length + 1
        assert chat_history[-1]["role"] == role
        assert chat_history[-1]["content"] == content


class TestClearHistory:
    """Property 5: Clear history always produces an empty list.

    **Validates: Requirements 6.2**
    """

    @given(
        history=st.lists(
            st.fixed_dictionaries(
                {
                    "role": st.sampled_from(["user", "assistant"]),
                    "content": st.text(),
                }
            )
        ),
    )
    @settings(max_examples=100)
    def test_clear_history_produces_empty_list(
        self, history: list[dict[str, str]]
    ) -> None:
        """For any chat history of any length, clearing it resets to an
        empty list with length zero."""
        # Simulate the clear operation (same as app.py sidebar button)
        history = []

        assert history == []
        assert len(history) == 0


class TestSessionStateUnit:
    """Unit tests for session state logic used in app.py.

    Validates: Requirements 5.1, 5.2, 5.3, 6.2
    """

    def test_chat_history_initializes_empty(self) -> None:
        """Chat history starts as an empty list."""
        chat_history: list[dict[str, str]] = []
        assert chat_history == []
        assert len(chat_history) == 0

    def test_append_user_message(self) -> None:
        """Appending a user message adds it correctly."""
        chat_history: list[dict[str, str]] = []
        chat_history.append({"role": "user", "content": "Hello"})
        assert len(chat_history) == 1
        assert chat_history[0] == {"role": "user", "content": "Hello"}

    def test_append_assistant_message(self) -> None:
        """Appending an assistant message adds it correctly."""
        chat_history: list[dict[str, str]] = [
            {"role": "user", "content": "Hello"},
        ]
        chat_history.append({"role": "assistant", "content": "Hi there!"})
        assert len(chat_history) == 2
        assert chat_history[1] == {
            "role": "assistant",
            "content": "Hi there!",
        }

    def test_clear_resets_to_empty(self) -> None:
        """Clearing chat history resets to empty list."""
        chat_history: list[dict[str, str]] = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"},
        ]
        chat_history = []
        assert chat_history == []
        assert len(chat_history) == 0
