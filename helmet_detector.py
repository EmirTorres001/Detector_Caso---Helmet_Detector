import flet as ft
import cv2
import numpy as np
import threading
import time
import logging
import os
from datetime import datetime
import base64
import io
from PIL import Image
import requests
import zipfile

class HelmetDetector:
    def __init__(self):
        self.is_detecting = False
        self.cap = None
        self.net = None
        self.output_layers = None
        self.classes = None
        self.colors = None
        self.confidence_threshold = 0.5
        self.nms_threshold = 0.4
        self.setup_logging()
        self.load_yolo_model()
        
    def setup_logging(self):
        """Configurar sistema de logs"""
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        log_filename = f"logs/helmet_detection_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            filename=log_filename,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
    def download_yolo_model(self):
        """Descargar modelo YOLO si no existe"""
        model_dir = "yolo_model"
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
            
        files = {
            'yolov3.weights': 'https://pjreddie.com/media/files/yolov3.weights',
            'yolov3.cfg': 'https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg',
            'coco.names': 'https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names'
        }
        
        for filename, url in files.items():
            filepath = os.path.join(model_dir, filename)
            if not os.path.exists(filepath):
                print(f"Descargando {filename}...")
                try:
                    response = requests.get(url, stream=True)
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                except Exception as e:
                    print(f"Error descargando {filename}: {e}")
                    
    def load_yolo_model(self):
        """Cargar modelo YOLO para detección"""
        try:
            # Intentar descargar modelo si no existe
            self.download_yolo_model()
            
            # Cargar red neuronal
            weights_path = "yolo_model/yolov3.weights"
            config_path = "yolo_model/yolov3.cfg"
            names_path = "yolo_model/coco.names"
            
            if os.path.exists(weights_path) and os.path.exists(config_path):
                self.net = cv2.dnn.readNet(weights_path, config_path)
                layer_names = self.net.getLayerNames()
                self.output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers().flatten()]
                
                # Cargar clases
                if os.path.exists(names_path):
                    with open(names_path, "r") as f:
                        self.classes = [line.strip() for line in f.readlines()]
                else:
                    # Clases básicas si no se puede cargar el archivo
                    self.classes = ["person", "helmet"]
                    
                self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))
                print("Modelo YOLO cargado exitosamente")
            else:
                print("No se pudo cargar el modelo YOLO, usando detección básica")
                self.net = None
                
        except Exception as e:
            print(f"Error cargando modelo YOLO: {e}")
            self.net = None
    
    def detect_helmet_basic(self, frame):
        """Detección básica usando características simples"""
        # Convertir a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detectar rostros usando Haar Cascade
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        helmet_detected = False
        
        for (x, y, w, h) in faces:
            # Área arriba de la cara donde estaría el casco
            helmet_region = frame[max(0, y-50):y+20, x:x+w]
            
            if helmet_region.size > 0:
                # Análisis de color - buscar colores típicos de cascos
                hsv = cv2.cvtColor(helmet_region, cv2.COLOR_BGR2HSV)
                
                # Rangos de colores para cascos (amarillo, blanco, naranja, etc.)
                helmet_colors = [
                    ([20, 100, 100], [30, 255, 255]),  # Amarillo
                    ([0, 0, 200], [180, 30, 255]),     # Blanco
                    ([10, 100, 100], [25, 255, 255])   # Naranja
                ]
                
                for lower, upper in helmet_colors:
                    mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
                    if cv2.countNonZero(mask) > helmet_region.shape[0] * helmet_region.shape[1] * 0.3:
                        helmet_detected = True
                        break
                        
                # Dibujar rectángulo alrededor de la cara
                color = (0, 255, 0) if helmet_detected else (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                
        return frame, helmet_detected
    
    def detect_helmet_yolo(self, frame):
        """Detección usando YOLO"""
        height, width, channels = frame.shape
        
        # Preparar imagen para YOLO
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.output_layers)
        
        # Información de detecciones
        class_ids = []
        confidences = []
        boxes = []
        helmet_detected = False
        
        # Procesar detecciones
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > self.confidence_threshold:
                    # Coordenadas del objeto
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    # Coordenadas del rectángulo
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # Aplicar Non-Maximum Suppression
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence_threshold, self.nms_threshold)
        
        # Dibujar detecciones
        if len(indexes) > 0:
            for i in indexes.flatten():
                x, y, w, h = boxes[i]
                label = str(self.classes[class_ids[i]]) if class_ids[i] < len(self.classes) else "unknown"
                confidence = confidences[i]
                
                # Verificar si es una persona y buscar casco
                if label == "person" or "helmet" in label.lower():
                    # Analizar región superior para casco
                    helmet_region = frame[max(0, y-20):y+h//3, x:x+w]
                    if self.analyze_helmet_region(helmet_region):
                        helmet_detected = True
                        color = (0, 255, 0)  # Verde
                    else:
                        color = (0, 0, 255)  # Rojo
                        
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, f"{label}: {confidence:.2f}", (x, y - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame, helmet_detected
    
    def analyze_helmet_region(self, region):
        """Analizar región específica para detectar casco"""
        if region.size == 0:
            return False
            
        # Análisis de color y textura
        hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
        
        # Detectar colores típicos de cascos
        helmet_masks = []
        
        # Amarillo
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([30, 255, 255])
        helmet_masks.append(cv2.inRange(hsv, lower_yellow, upper_yellow))
        
        # Blanco
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])
        helmet_masks.append(cv2.inRange(hsv, lower_white, upper_white))
        
        # Naranja
        lower_orange = np.array([10, 100, 100])
        upper_orange = np.array([25, 255, 255])
        helmet_masks.append(cv2.inRange(hsv, lower_orange, upper_orange))
        
        # Verificar si algún color de casco está presente
        total_pixels = region.shape[0] * region.shape[1]
        for mask in helmet_masks:
            helmet_pixels = cv2.countNonZero(mask)
            if helmet_pixels > total_pixels * 0.25:  # 25% de la región
                return True
                
        return False
    
    def process_frame(self, frame):
        """Procesar frame para detección de casco"""
        try:
            if self.net is not None:
                return self.detect_helmet_yolo(frame)
            else:
                return self.detect_helmet_basic(frame)
        except Exception as e:
            print(f"Error procesando frame: {e}")
            return frame, False

class HelmetDetectorApp:
    def __init__(self):
        self.detector = HelmetDetector()
        self.page = None
        self.camera_view = None
        self.status_text = None
        self.status_icon = None
        self.start_stop_btn = None
        self.detection_thread = None
        self.last_detection_result = False
        self.last_detection_time = time.time()
        
    def create_placeholder_image(self):
        """Crear imagen placeholder cuando no hay cámara activa"""
        try:
            # Crear imagen simple de 400x300 con texto
            img = Image.new('RGB', (400, 300), color='#2d2d2d')
            
            # Convertir a base64
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG')
            img_str = base64.b64encode(img_buffer.getvalue()).decode()
            
            return img_str
        except Exception as e:
            print(f"Error creando placeholder: {e}")
            # Imagen base64 mínima de 1x1 pixel como fallback
            return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    def main(self, page: ft.Page):
        self.page = page
        page.title = "Detector de Casco de Seguridad"
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = "#1a1a1a"
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.padding = 20
        
        # Barra superior
        header = ft.Container(
            content=ft.Text(
                "🛡️ Detector de Casco",
                size=24,
                weight=ft.FontWeight.BOLD,
                color="#ffffff"
            ),
            alignment=ft.alignment.center,
            padding=ft.padding.only(bottom=20)
        )
        
        # Vista de cámara con imagen placeholder
        self.camera_view = ft.Image(
            src_base64=self.create_placeholder_image(),
            width=400,
            height=300,
            fit=ft.ImageFit.CONTAIN,
            border_radius=10
        )
        
        camera_container = ft.Container(
            content=self.camera_view,
            bgcolor="#2d2d2d",
            border_radius=10,
            padding=10,
            alignment=ft.alignment.center
        )
        
        # Estado de detección
        self.status_icon = ft.Icon(
            ft.icons.HELP_OUTLINE,
            color="#888888",
            size=40
        )
        
        self.status_text = ft.Text(
            "Presiona Iniciar para comenzar",
            size=18,
            color="#888888",
            text_align=ft.TextAlign.CENTER
        )
        
        status_container = ft.Container(
            content=ft.Column([
                self.status_icon,
                self.status_text
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            padding=20
        )
        
        # Botones
        self.start_stop_btn = ft.ElevatedButton(
            text="Iniciar Detección",
            icon=ft.icons.PLAY_ARROW,
            on_click=self.toggle_detection,
            bgcolor="#4CAF50",
            color="#ffffff",
            width=200,
            height=50
        )
        
        capture_btn = ft.ElevatedButton(
            text="Capturar",
            icon=ft.icons.CAMERA_ALT,
            on_click=self.capture_image,
            bgcolor="#2196F3",
            color="#ffffff",
            width=200,
            height=50
        )
        
        buttons_row = ft.Row([
            self.start_stop_btn,
            capture_btn
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        
        # Layout principal
        main_column = ft.Column([
            header,
            camera_container,
            status_container,
            buttons_row
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
        
        page.add(main_column)
        page.update()
        
    def toggle_detection(self, e):
        """Iniciar/detener detección"""
        if not self.detector.is_detecting:
            self.start_detection()
        else:
            self.stop_detection()
    
    def start_detection(self):
        """Iniciar detección"""
        try:
            self.detector.cap = cv2.VideoCapture(0)
            if not self.detector.cap.isOpened():
                self.show_error("No se pudo acceder a la cámara")
                return
                
            # Configurar cámara para mejor rendimiento
            self.detector.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.detector.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.detector.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.detector.is_detecting = True
            
            # Actualizar UI
            self.start_stop_btn.text = "Detener Detección"
            self.start_stop_btn.icon = ft.icons.STOP
            self.start_stop_btn.bgcolor = "#F44336"
            self.page.update()
            
            # Iniciar hilo de detección
            self.detection_thread = threading.Thread(target=self.detection_loop)
            self.detection_thread.daemon = True
            self.detection_thread.start()
            
            print("Detección iniciada")
            
        except Exception as e:
            self.show_error(f"Error iniciando detección: {e}")
    
    def stop_detection(self):
        """Detener detección"""
        self.detector.is_detecting = False
        
        if self.detector.cap:
            self.detector.cap.release()
            
        # Actualizar UI
        self.start_stop_btn.text = "Iniciar Detección"
        self.start_stop_btn.icon = ft.icons.PLAY_ARROW
        self.start_stop_btn.bgcolor = "#4CAF50"
        
        self.status_text.value = "Detección detenida"
        self.status_text.color = "#888888"
        self.status_icon.name = ft.icons.HELP_OUTLINE
        self.status_icon.color = "#888888"
        
        # Restaurar imagen placeholder
        self.camera_view.src_base64 = self.create_placeholder_image()
        
        self.page.update()
        print("Detección detenida")
    
    def detection_loop(self):
        """Bucle principal de detección"""
        frame_count = 0
        fps_start_time = time.time()
        
        while self.detector.is_detecting:
            try:
                ret, frame = self.detector.cap.read()
                if not ret:
                    continue
                
                # Procesar cada 2 frames para mejor rendimiento
                if frame_count % 2 == 0:
                    # Procesar detección
                    processed_frame, helmet_detected = self.detector.process_frame(frame)
                    
                    # Actualizar estado si cambió
                    if helmet_detected != self.last_detection_result:
                        self.last_detection_result = helmet_detected
                        self.last_detection_time = time.time()
                        self.update_detection_status(helmet_detected)
                        self.log_detection(helmet_detected)
                    
                    # Convertir frame a base64 para mostrar
                    self.update_camera_view(processed_frame)
                
                frame_count += 1
                
                # Calcular FPS cada segundo
                if time.time() - fps_start_time >= 1.0:
                    fps = frame_count / (time.time() - fps_start_time)
                    print(f"FPS: {fps:.1f}")
                    frame_count = 0
                    fps_start_time = time.time()
                
                # Pequeña pausa para no sobrecargar el sistema
                time.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                print(f"Error en bucle de detección: {e}")
                time.sleep(0.1)
    
    def update_camera_view(self, frame):
        """Actualizar vista de cámara"""
        try:
            # Redimensionar frame para mejor rendimiento
            frame_resized = cv2.resize(frame, (400, 300))
            
            # Convertir a formato RGB
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            
            # Convertir a PIL Image
            pil_image = Image.fromarray(frame_rgb)
            
            # Convertir a base64
            img_buffer = io.BytesIO()
            pil_image.save(img_buffer, format='JPEG', quality=85)
            img_str = base64.b64encode(img_buffer.getvalue()).decode()
            
            # Actualizar imagen en UI
            if self.camera_view:
                self.camera_view.src_base64 = img_str
                self.camera_view.update()
            
        except Exception as e:
            print(f"Error actualizando vista de cámara: {e}")
            # Usar imagen placeholder en caso de error
            if self.camera_view:
                self.camera_view.src_base64 = self.create_placeholder_image()
                self.camera_view.update()
    
    def update_detection_status(self, helmet_detected):
        """Actualizar estado de detección en UI"""
        try:
            if helmet_detected:
                self.status_text.value = "✅ Casco Detectado"
                self.status_text.color = "#4CAF50"
                self.status_icon.name = ft.icons.VERIFIED_USER
                self.status_icon.color = "#4CAF50"
            else:
                self.status_text.value = "❌ Sin Casco"
                self.status_text.color = "#F44336"
                self.status_icon.name = ft.icons.WARNING
                self.status_icon.color = "#F44336"
                
            self.page.update()
            
        except Exception as e:
            print(f"Error actualizando estado: {e}")
    
    def log_detection(self, helmet_detected):
        """Registrar detección en logs"""
        status = "CASCO_DETECTADO" if helmet_detected else "SIN_CASCO"
        logging.info(f"Detección: {status}")
        
    def capture_image(self, e):
        """Capturar imagen actual"""
        if self.detector.cap and self.detector.is_detecting:
            try:
                ret, frame = self.detector.cap.read()
                if ret:
                    # Crear directorio de capturas
                    if not os.path.exists('capturas'):
                        os.makedirs('capturas')
                    
                    # Guardar imagen
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"capturas/captura_{timestamp}.jpg"
                    cv2.imwrite(filename, frame)
                    
                    print(f"Imagen guardada: {filename}")
                    logging.info(f"Captura guardada: {filename}")
                    
            except Exception as e:
                print(f"Error capturando imagen: {e}")
    
    def show_error(self, message):
        """Mostrar mensaje de error"""
        self.status_text.value = f"Error: {message}"
        self.status_text.color = "#F44336"
        self.page.update()

def main(page: ft.Page):
    app = HelmetDetectorApp()
    app.main(page)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")