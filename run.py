import os
import sys

# Force working directory to the project root so all relative paths resolve correctly
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from vacantview.main import run_app

if __name__ == "__main__":
    run_app()
