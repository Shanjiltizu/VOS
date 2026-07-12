from core.engine import CoreEngine
from config import APP_NAME, VERSION


def start_vos():
    print("=" * 50)
    print(f"🚀 Starting {APP_NAME} {VERSION}")
    print("=" * 50)

    core = CoreEngine()
    core.start()

    print()
    print("👋 Hey mate.")
    print("Ready to build something awesome?")


if __name__ == "__main__":
    start_vos()