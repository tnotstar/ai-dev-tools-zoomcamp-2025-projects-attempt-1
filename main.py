import subprocess
import time
import os
import signal
import sys

def run_servers():
    env = os.environ.copy()
    
    # Processes
    procs = []
    
    try:
        # Run backend: Change dir to backend so uv finds backend/pyproject.toml
        # Using uvicorn with WSGI interface and reload enabled
        backend_cmd = ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5001", "--reload", "--interface", "wsgi"]
        backend_proc = subprocess.Popen(backend_cmd, env=env, cwd=os.path.join(os.getcwd(), "backend"))
        procs.append(backend_proc)
        
        # Give backend a moment to initialize
        time.sleep(2)

        print("[INFO] Starting Frontend Server (Port 5000)...")
        # Run frontend: Change dir to frontend so uv finds frontend/pyproject.toml
        frontend_cmd = ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--reload", "--interface", "wsgi"]
        frontend_proc = subprocess.Popen(frontend_cmd, env=env, cwd=os.path.join(os.getcwd(), "frontend"))
        procs.append(frontend_proc)
        
        print("\n[SUCCESS] Environment is running!")
        print("Press Ctrl+C to stop.\n")
        
        # Monitor Loop
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print("[WARN] Backend process exited unexpectedly.")
                break
            if frontend_proc.poll() is not None:
                print("[WARN] Frontend process exited unexpectedly.")
                break

    except KeyboardInterrupt:
        print("\n[INFO] Stopping servers...")
    finally:
        for p in procs:
            if p.poll() is None:
                p.terminate()
        print("[INFO] Shutdown complete.")

if __name__ == "__main__":
    run_servers()
