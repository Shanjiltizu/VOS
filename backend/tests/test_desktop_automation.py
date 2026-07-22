import sys
import unittest
from pathlib import Path
from unittest.mock import patch

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

import main
from modules.atlas import Atlas
from modules.cortex import Cortex
from modules.titan import Titan


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


class ScreenAwarenessTests(unittest.TestCase):
    def test_cortex_recognizes_screen_awareness_intents(self):
        cortex = Cortex()

        self.assertEqual(cortex.understand("take screenshot")["intent"], "INTENT_CAPTURE_SCREEN")
        self.assertEqual(cortex.understand("capture active window")["intent"], "INTENT_CAPTURE_WINDOW")
        self.assertEqual(cortex.understand("what is on my screen")["intent"], "INTENT_DESCRIBE_SCREEN")
        self.assertEqual(cortex.understand("show current resolution")["intent"], "INTENT_GET_SCREEN_INFO")

    def test_cortex_recognizes_ocr_intents(self):
        cortex = Cortex()

        self.assertEqual(cortex.understand("read my screen")["intent"], "INTENT_READ_SCREEN")
        self.assertEqual(cortex.understand("read current window")["intent"], "INTENT_READ_WINDOW")
        self.assertEqual(cortex.understand("extract text")["intent"], "INTENT_EXTRACT_TEXT")
        self.assertEqual(cortex.understand("read highlighted text")["intent"], "INTENT_READ_TEXT")

    def test_atlas_creates_screen_awareness_plans(self):
        atlas = Atlas()

        self.assertEqual(atlas.plan({"intent": "INTENT_CAPTURE_SCREEN"})["action"], "CAPTURE_SCREEN")
        self.assertEqual(atlas.plan({"intent": "INTENT_CAPTURE_WINDOW"})["action"], "CAPTURE_ACTIVE_WINDOW")
        self.assertEqual(atlas.plan({"intent": "INTENT_GET_SCREEN_INFO"})["action"], "GET_SCREEN_INFO")

    def test_atlas_creates_ocr_plans(self):
        atlas = Atlas()

        self.assertEqual(atlas.plan({"intent": "INTENT_READ_SCREEN"})["action"], "OCR_SCREEN")
        self.assertEqual(atlas.plan({"intent": "INTENT_READ_WINDOW"})["action"], "OCR_WINDOW")
        self.assertEqual(atlas.plan({"intent": "INTENT_EXTRACT_TEXT"})["action"], "OCR_IMAGE")

    def test_titan_returns_screen_metadata(self):
        titan = Titan()
        result = titan.execute({"action": "GET_SCREEN_INFO"})

        self.assertEqual(result["status"], "SUCCESS")
        self.assertIn("width", result["metadata"])
        self.assertIn("height", result["metadata"])
        self.assertIn("platform", result["metadata"])

    def test_titan_handles_ocr_without_screenshot(self):
        titan = Titan()
        result = titan.execute({"action": "OCR_SCREEN"})

        self.assertEqual(result["status"], "FAILED")
        self.assertIn("screenshot", result["message"].lower())


if __name__ == "__main__":
    unittest.main()
