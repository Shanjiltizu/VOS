import sys
import unittest
from pathlib import Path
from unittest.mock import patch

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

import main


class StartVOSTests(unittest.TestCase):
    def test_start_vos_returns_failure_when_required_modules_are_missing(self):
        class DummyCore:
            def __init__(self):
                self.modules = [object()]

            def start(self):
                return None

        with patch.object(main, "CoreEngine", return_value=DummyCore()):
            with patch.object(main, "Cortex", return_value=object()):
                result = main.start_vos()

        self.assertEqual(result["status"], "FAILED")
        self.assertIn("required module", result["message"].lower())

    def test_start_vos_returns_success_for_supported_pipeline(self):
        class DummyEcho:
            def __init__(self):
                self.messages = []

            def listen(self):
                return "open chrome"

            def speak(self, message):
                self.messages.append(message)

        class DummyAtlas:
            def plan(self, task):
                return {"action": "LAUNCH_APP", "app": "chrome", "label": "Chrome"}

        class DummyTitan:
            def execute(self, plan):
                return {"status": "SUCCESS", "message": "Opening Chrome."}

        class DummyCore:
            def __init__(self):
                self.modules = [DummyEcho(), DummyAtlas(), DummyTitan()]

            def start(self):
                return None

        dummy_echo = DummyEcho()

        class DummyCoreWithEcho(DummyCore):
            def __init__(self):
                self.modules = [dummy_echo, DummyAtlas(), DummyTitan()]

        with patch.object(main, "CoreEngine", return_value=DummyCoreWithEcho()):
            with patch.object(main, "Cortex", return_value=type("DummyCortex", (), {"understand": lambda self, command: {"intent": "OPEN_APP", "target": command}})()):
                result = main.start_vos()

        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(dummy_echo.messages[-1], "Opening Chrome.")


if __name__ == "__main__":
    unittest.main()
