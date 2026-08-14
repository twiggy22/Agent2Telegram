import unittest

from agent2telegram.readers import CodexReader


class CodexReaderTests(unittest.TestCase):
    def test_new_response_item_assistant_message_is_forwarded(self):
        events = list(CodexReader().parse({
            "type": "response_item",
            "payload": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "hello from Codex"}],
            },
        }))
        self.assertEqual([(e.kind, e.text) for e in events], [("text", "hello from Codex")])

    def test_new_response_item_user_message_is_detected(self):
        events = list(CodexReader().parse({
            "type": "response_item",
            "payload": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "hello to Codex"}],
            },
        }))
        self.assertEqual([(e.kind, e.text) for e in events], [("user", "hello to Codex")])


if __name__ == "__main__":
    unittest.main()
