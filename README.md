# SecureBrain
---

#### **Descripción General**
El sistema es una solución de seguridad que detecta movimientos y analiza comportamientos en tiempo real utilizando una cámara conectada. Ante actividades sospechosas, genera alertas visuales y realiza una llamada al propietario utilizando el protocolo SIP mediante Linphone.

---

### **Componentes Principales**

#### **1. Detección de Movimiento (`motion_detection.py`)**
- **Responsabilidad:** Detectar movimientos en la cámara.
- **Flujo Principal:**
  1. Captura imágenes de la cámara en tiempo real.
  2. Detecta cambios entre el primer frame y los actuales (movimiento).
  3. Dibuja contornos sobre las áreas donde detecta movimiento.
  4. Si una persona permanece en el área por más de un tiempo configurado (`presence_time`), activa el análisis de comportamiento.

- **Configuración:**
  - `min_area`: Tamaño mínimo de un área para considerarse movimiento.
  - `max_area`: Tamaño máximo de un área para evitar falsos positivos.
  - `sensitivity`: Sensibilidad para detectar movimiento.
  - `presence_time`: Tiempo en segundos que una persona debe estar presente para ser considerada.
  - `frame_skip`: Procesar 1 de cada N frames.

---

#### **2. Análisis de Comportamiento (`behavior_analysis.py`)**
- **Responsabilidad:** Evaluar si el comportamiento detectado es sospechoso.
- **Flujo Principal:**
  1. Utiliza detección de objetos para identificar personas u otros elementos.
  2. Analiza la postura de la persona mediante MediaPipe (ej., detecta si está agachado).
  3. Si el comportamiento cumple con criterios definidos, lo marca como sospechoso.

---

#### **3. Notificaciones (`notification.py`)**
- **Responsabilidad:** Generar alertas y realizar llamadas en caso de detectar actividad sospechosa.
- **Flujo Principal:**
  1. Genera un mensaje de voz con `gTTS` y lo guarda como archivo de audio.
  2. Realiza una llamada SIP al propietario utilizando Linphone y reproduce el mensaje.

- **Configuración de Linphone:**
  - `sip_address`: Dirección SIP del sistema.
  - `password`: Contraseña para autenticarse en el servidor SIP.
  - `call_to`: Dirección SIP del propietario a quien llamar.
  - `audio_file`: Nombre del archivo de audio generado.

---

#### **4. Interfaz Gráfica (`mainexe.py`)**
- **Responsabilidad:** Proporcionar una interfaz de usuario sencilla para interactuar con el sistema.
- **Funciones Principales:**
  - **Iniciar Detección:** Activa la detección de movimiento.
  - **Detener Detección:** Detiene la captura y análisis de la cámara.
  - **Habilitar/Deshabilitar Notificaciones:** Alterna la funcionalidad de notificaciones.
  - **Logs en Tiempo Real:** Muestra los logs recientes en la interfaz.
  - **Configuración:** Permite ajustar parámetros como la sensibilidad y el tiempo mínimo visible.

---

### **Instalación y Configuración**
1. **Dependencias:**
   - Python 3.x
   - OpenCV
   - gTTS
   - MediaPipe
   - Linphone instalado y configurado.

2. **Archivos y Carpetas:**
   - `logs/`: Almacena los logs generados por el sistema.
   - `models/`: Contiene los modelos de YOLO para la detección de objetos.
   - `voice_message.wav`: Archivo de audio generado para las llamadas.

3. **Configuraciones Clave:**
   - Actualizar las credenciales de Linphone en el archivo `notification.py`.

---

### **Flujo del Sistema**
1. **Inicio del Sistema:**
   - El usuario inicia la detección de movimiento desde la interfaz gráfica.
   - La cámara comienza a capturar frames.

2. **Detección de Movimiento:**
   - Identifica áreas de movimiento.
   - Si detecta presencia prolongada, analiza el comportamiento.

3. **Análisis de Comportamiento:**
   - Determina si el comportamiento es sospechoso basándose en posturas y permanencia.

4. **Notificación:**
   - Si se detecta un comportamiento sospechoso:
     - Se genera un mensaje de voz.
     - Realiza una llamada al propietario.

---

### **Próximos Pasos y Mejoras**
- **Optimización del Procesamiento:**
  - Reducir el consumo de recursos optimizando el análisis de frames.
- **Integración con Notificaciones Avanzadas:**
  - Enviar alertas adicionales como correos electrónicos o mensajes SMS.
- **Almacenamiento en la Nube:**
  - Subir grabaciones y fotos de actividad sospechosa a un servidor remoto.

---

### **Notas Finales**
Este sistema combina detección de movimiento, análisis de comportamiento y comunicación SIP para crear una solución de seguridad eficiente. Es extensible y adaptable a diferentes escenarios de uso.
