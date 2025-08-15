#!/usr/bin/env python3
"""
Setup script para Helmet Detector
Automatiza la instalación y configuración del proyecto
"""

import os
import sys
import subprocess
import platform
import urllib.request
from pathlib import Path

def print_step(message):
    """Imprimir paso del setup"""
    print(f"\n🔧 {message}")
    print("-" * 50)

def run_command(command, check=True):
    """Ejecutar comando del sistema"""
    print(f"Ejecutando: {command}")
    try:
        result = subprocess.run(command, shell=True, check=check, 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando comando: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Verificar versión de Python"""
    print_step("Verificando versión de Python")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"Versión actual: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} OK")

def create_virtual_environment():
    """Crear entorno virtual"""
    print_step("Creando entorno virtual")
    
    if os.path.exists("venv"):
        print("ℹ️ El entorno virtual ya existe")
        return True
    
    if not run_command(f"{sys.executable} -m venv venv"):
        print("❌ Error creando entorno virtual")
        return False
    
    print("✅ Entorno virtual creado")
    return True

def get_activation_command():
    """Obtener comando de activación según el SO"""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def install_dependencies():
    """Instalar dependencias"""
    print_step("Instalando dependencias")
    
    # Determinar ejecutable de pip
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    # Actualizar pip
    if not run_command(f"{pip_cmd} install --upgrade pip"):
        print("⚠️ Advertencia: No se pudo actualizar pip")
    
    # Instalar dependencias principales
    dependencies = [
        "flet>=0.24.1",
        "opencv-python>=4.8.1.78",
        "numpy>=1.24.3",
        "Pillow>=10.0.0",
        "requests>=2.31.0"
    ]
    
    for dep in dependencies:
        print(f"Instalando {dep}...")
        if not run_command(f"{pip_cmd} install {dep}"):
            print(f"❌ Error instalando {dep}")
            return False
    
    # Instalar dependencias específicas del SO
    system = platform.system()
    if system == "Linux":
        print("Instalando dependencias para Linux...")
        run_command("sudo apt-get update", check=False)
        run_command("sudo apt-get install -y python3-opencv libglib2.0-0 libsm6 libxext6 libxrender-dev libgl1-mesa-glx", check=False)
    
    print("✅ Dependencias instaladas")
    return True

def create_directories():
    """Crear directorios necesarios"""
    print_step("Creando directorios")
    
    dirs = ["yolo_model", "logs", "capturas", "assets"]
    
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Directorio '{dir_name}' creado")

def download_yolo_model():
    """Descargar modelo YOLO"""
    print_step("Descargando modelo YOLO")
    
    model_dir = Path("yolo_model")
    
    files = {
        'yolov3.cfg': 'https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg',
        'coco.names': 'https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names'
    }
    
    # Descargar archivos pequeños
    for filename, url in files.items():
        filepath = model_dir / filename
        if not filepath.exists():
            print(f"Descargando {filename}...")
            try:
                urllib.request.urlretrieve(url, filepath)
                print(f"✅ {filename} descargado")
            except Exception as e:
                print(f"❌ Error descargando {filename}: {e}")
    
    # Información sobre yolov3.weights
    weights_path = model_dir / "yolov3.weights"
    if not weights_path.exists():
        print("\n📝 NOTA IMPORTANTE:")
        print("El archivo yolov3.weights (~248MB) se descargará automáticamente")
        print("la primera vez que ejecutes la aplicación.")
        print("Si tienes conexión lenta, puedes descargarlo manualmente desde:")
        print("https://pjreddie.com/media/files/yolov3.weights")
        print(f"y guardarlo en: {weights_path}")

def create_run_scripts():
    """Crear scripts de ejecución"""
    print_step("Creando scripts de ejecución")
    
    # Script para Windows
    with open("run_helmet_detector.bat", "w") as f:
        f.write("""@echo off
echo Iniciando Detector de Casco...
call venv\\Scripts\\activate
python helmet_detector.py
pause
""")
    print("✅ Script para Windows creado (run_helmet_detector.bat)")
    
    # Script para Linux/macOS
    with open("run_helmet_detector.sh", "w") as f:
        f.write("""#!/bin/bash
echo "Iniciando Detector de Casco..."
source venv/bin/activate
python helmet_detector.py
""")
    
    # Hacer ejecutable en Linux/macOS
    if platform.system() != "Windows":
        os.chmod("run_helmet_detector.sh", 0o755)
    print("✅ Script para Linux/macOS creado (run_helmet_detector.sh)")

def create_build_scripts():
    """Crear scripts de compilación"""
    print_step("Creando scripts de compilación")
    
    # Script de compilación para escritorio
    with open("build_desktop.py", "w") as f:
        f.write("""#!/usr/bin/env python3
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
""")
    print("✅ Script de compilación para escritorio creado")

def print_completion_message():
    """Mostrar mensaje de finalización"""
    print("\n" + "=" * 60)
    print("🎉 ¡INSTALACIÓN COMPLETADA!")
    print("=" * 60)
    
    activation_cmd = get_activation_command()
    
    print(f"""
📋 PRÓXIMOS PASOS:

1️⃣ Activar entorno virtual:
   {activation_cmd}

2️⃣ Ejecutar la aplicación:
   python helmet_detector.py

3️⃣ O usar los scripts creados:
   • Windows: run_helmet_detector.bat
   • Linux/macOS: ./run_helmet_detector.sh

🔧 COMANDOS ÚTILES:

• Modo web: flet run helmet_detector.py --web
• Compilar ejecutable: python build_desktop.py
• Compilar Android: flet build apk

📁 ARCHIVOS CREADOS:
• venv/ - Entorno virtual
• yolo_model/ - Modelos de IA
• logs/ - Archivos de registro
• capturas/ - Imágenes capturadas
• run_helmet_detector.* - Scripts de ejecución

ℹ️ NOTAS:
• El modelo YOLO se descargará automáticamente al primer uso
• La aplicación requiere acceso a la cámara
• Los logs se guardan automáticamente en logs/

🆘 SOPORTE:
Si encuentras problemas, revisa los logs o ejecuta:
python helmet_detector.py

¡Disfruta detectando cascos de seguridad! 🛡️
""")

def main():
    """Función principal del setup"""
    print("🛡️ SETUP: DETECTOR DE CASCO DE SEGURIDAD")
    print("=" * 60)
    
    try:
        check_python_version()
        create_virtual_environment()
        install_dependencies()
        create_directories()
        download_yolo_model()
        create_run_scripts()
        create_build_scripts()
        print_completion_message()
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error durante el setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()