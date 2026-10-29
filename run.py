#!/usr/bin/env python3
"""
Launcher for Physical Therapy Gait Analysis Application
"""
import os
import sys

# Ensure matplotlib and app directories are configured
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_cache"
os.makedirs("/tmp/matplotlib_cache", exist_ok=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Gait Analysis Physical Therapy Server on http://localhost:{port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port, log_level="info")
