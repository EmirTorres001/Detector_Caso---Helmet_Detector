[app]

# (str) Título de tu aplicación
title = Helmet Detector

# (str) Nombre del paquete
package.name = helmetdetector

# (str) Dominio del paquete (necesario para publicar en Google Play)
package.domain = com.helmetdetector

# (str) Directorio fuente donde viven los archivos de la aplicación
source.dir = .

# (list) Patrones de archivos fuente a incluir
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,cfg,names,weights,ttf

# (str) Versión de la aplicación
version = 1.0

# (list) Requisitos de la aplicación
# Nota: opencv4 se usa en lugar de opencv-python para Android
requirements = python3,kivy,flet,opencv4,numpy,pillow,requests,plyer

# (str) Icono de la aplicación
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indica si la aplicación debe estar en modo fullscreen o no
fullscreen = 0

[buildozer]

# (int) Log level (0 = solo errores y advertencias, 1 = info, 2 = debug)
log_level = 2

# (int) Mostrar advertencias usando el color (0 = no, 1 = sí)
warn_on_root = 1

[app:android]

# (bool) Habilitar respaldo de Android Auto (Android API 23+)
android.allow_backup = True

# (str) XML de archivo de configuración de respaldo de Android
#android.backup_rules = 

# (str) Versión mínima de API que se requiere para ejecutar la aplicación
android.minapi = 21

# (str) Versión de API de Android para compilar
android.api = 31

# (str) Versión de Android NDK a usar
android.ndk = 25b

# (bool) Usar --private para el almacén de datos (True) o --dir (False)
android.private_storage = True

# (str) Directorio de Android NDK (si vacío, se descargará automáticamente)
#android.ndk_path = 

# (str) Directorio de Android SDK (si vacío, se descargará automáticamente)
#android.sdk_path = 

# (str) ANT directory (if empty, it will be automatically downloaded)
#android.ant_path = 

# (bool) Si es True, entonces omite el intent filter requerido desde Android manifest
android.skip_update = False

# (bool) Si es True, entonces crea un archivo AAB, en lugar de APK
#android.release_artifact = aab

# (str) Modo de compilación para la aplicación (debug o release)
android.compile_mode = debug

# Lista de permisos Java (.java files)
#android.add_java_files = 

# (str) OUYA Console category
#android.ouya.category = GAME

# (str) Archivo donde almacenar la configuración de gradle
#android.gradle_properties = 

# Lista de dependencias gradle
#android.gradle_dependencies = 

# Lista de repositorios gradle
#android.gradle_repositories = 

# (bool) Habilitar AndroidX support
android.enable_androidx = True

# (bool) Habilitar Jetifier
android.enable_jetifier = True

# (list) Patrones para incluir en el directorio libs para Android
#android.add_libs_directory = 

# (list) Patrones para incluir en el directorio src para Android
#android.add_src = 

# (list) Patrones de archivos a incluir en el directorio libs para Android
#android.add_libs = 

# (list) Módulos Gradle para agregar
#android.gradle_modules = 

# (bool) Copy library instead of making a libpymodules.so
#android.copy_libs = 1

# (str) El contenido de la cadena de Android / manifest de la aplicación
#android.manifest.intent_filters = 

# (str) El contenido de la actividad de Android / manifest
#android.manifest.activity_intent_filters = 

# (str) Configuración de metadatos de Android manifest.application
#android.manifest.application_metadata = 

# (str) Configuración de metadatos de Android manifest.activity
#android.manifest.activity_metadata = 

# (str) Configuración de hardware de Android manifest.activity
#android.manifest.hardware_acceleration = 

# (list) Permisos de Android
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET,ACCESS_NETWORK_STATE

# (int) Target Android API, should be as high as possible.
android.api_target = 31

# (str) Android entry point
#android.entrypoint = 

# (list) Lista de servicios de Android a crear por pythonforandroid
#android.services = 

# (str) Configuración del adaptive icon de Android
#android.adaptive_icon_background = #FFFFFF
#android.adaptive_icon_foreground = %(source.dir)s/data/icon_foreground.png

# (bool) copies OpenCV libraries into the APK
android.opencv = 1

[buildozer:global]

# (str) Ruta al directorio de buildozer (por defecto en ~/.buildozer)
#builddir = 

# (str) Ruta al repositorio de buildozer
#cache_dir = 

# (str) Ruta a los logs de compilación
#log_dir =