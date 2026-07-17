from modules.echo import Echo
from modules.atlas import Atlas
from modules.titan import Titan


class CoreEngine:

    def __init__(self):
        self.name = "VOS Core"

        self.modules = [
            Echo(),
            Atlas(),
            Titan(),
        ]

    def start(self):

        print("[CORE] Initializing...")
        print("✅ Core Ready")
        print()

        print("[CORE] Loading Modules...\n")

        for module in self.modules:
            module.start()

        print()
        print("✅ All Modules Loaded")
        