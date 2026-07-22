import sys

from core.engine import CoreEngine
from modules.echo import Echo
from modules.cortex import Cortex
from modules.atlas import Atlas
from modules.titan import Titan
from config import APP_NAME, VERSION


def _resolve_module(modules, required_methods):
    for module in modules or []:
        if module is None:
            continue
        if all(hasattr(module, method) for method in required_methods):
            return module
    return None


def start_vos():
    # Ensure console output supports Unicode emoji on Windows.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 50)
    print(f"🚀 Starting {APP_NAME} {VERSION}")
    print("=" * 50)

    try:
        core = CoreEngine()
        core.start()
    except Exception as error:
        message = f"Failed to initialize the VOS core engine: {error}"
        print(f"[VOS] {message}")
        return {"status": "FAILED", "message": message}

    cortex = _resolve_module(getattr(core, "modules", []), ["understand"])
    if cortex is None:
        try:
            cortex = Cortex()
        except Exception:
            cortex = None

    echo = _resolve_module(getattr(core, "modules", []), ["listen", "speak"])
    atlas = _resolve_module(getattr(core, "modules", []), ["plan"])
    titan = _resolve_module(getattr(core, "modules", []), ["execute"])

    if not all([cortex, echo, atlas, titan]):
        message = "Failed to initialize the required module pipeline."
        if echo is not None:
            try:
                echo.speak(message)
            except Exception:
                pass
        return {"status": "FAILED", "message": message}

    command = echo.listen()
    if not command:
        message = "I could not hear a command. Please try again with a microphone connected."
        echo.speak(message)
        return {"status": "FAILED", "message": message}

    task = cortex.understand(command)
    if not isinstance(task, dict):
        message = "The intent engine returned an invalid task."
        echo.speak(message)
        return {"status": "FAILED", "message": message}

    plan = atlas.plan(task)
    if not isinstance(plan, dict):
        message = "The planning engine returned an invalid plan."
        echo.speak(message)
        return {"status": "FAILED", "message": message}

    result = titan.execute(plan)
    if not isinstance(result, dict):
        result = {"status": "FAILED", "message": "The execution engine returned an invalid response."}

    response_message = result.get("message") or "Task completed."
    if echo is not None:
        echo.speak(response_message)

    return {
        "status": result.get("status", "SUCCESS"),
        "message": response_message,
        "task": task,
        "plan": plan,
        "result": result,
    }


if __name__ == "__main__":
    start_vos()
    