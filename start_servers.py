import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
PYTHON_EXEC = sys.executable

procs = []

def start(name, script):
    print(f"Starting {name}...")
    p = subprocess.Popen(
        [PYTHON_EXEC, str(PROJECT_ROOT / "mcp_servers" / script)],
        cwd=str(PROJECT_ROOT),
    )
    procs.append(p)
    return p

if __name__ == "__main__":
    start("database_server", "database_server.py")
    start("vector_server", "vector_server.py")
    print("Both servers starting. Press Ctrl+C to stop both.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping servers...")
        for p in procs:
            p.terminate()