from core.engine import CoreEngine
from modules.echo import Echo
from modules.cortex import Cortex
from modules.atlas import Atlas
from modules.titan import Titan
from config import APP_NAME, VERSION


def start_vos():
    print("=" * 50)
    print(f"🚀 Starting {APP_NAME} {VERSION}")
    print("=" * 50)

    core = CoreEngine()
    core.start()

    cortex = Cortex()

    echo = next(module for module in core.modules if isinstance(module, Echo))
    atlas = next(module for module in core.modules if isinstance(module, Atlas))
    titan = next(module for module in core.modules if isinstance(module, Titan))

    command = echo.listen()
    if not command:
        echo.speak("I could not hear a command. Please try again with a microphone connected.")
        return

    task = cortex.understand(command)
    plan = atlas.plan(task)
    result = titan.execute(plan)

    echo.speak(result["message"])


if __name__ == "__main__":
    start_vos()
    