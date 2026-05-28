import sys
import os

# Add schema-conversion-orchestrator/ to sys.path so module imports work
orchestrator_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if orchestrator_dir not in sys.path:
    sys.path.insert(0, orchestrator_dir)
