#!/usr/bin/env python3
import subprocess
import platform

def build_desktop():
    system = platform.system()
    
    if system == "Windows":
        icon = "--icon app_icon.ico" if os.path.exists("app_icon.ico") else ""
    elif system == "Darwin":  # macOS
        icon = "--icon app_icon.icns" if os.path.exists("app_icon.icns") else ""
    else:
        icon = ""
    
    cmd = f"flet pack helmet_detector.py --name HelmetDetector {icon}"
    print(f"Ejecutando: {cmd}")
    subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    import os
    build_desktop()
