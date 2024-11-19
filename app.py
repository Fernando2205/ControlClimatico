from flask import Flask, render_template, request
from sensor import Sensor
from controlador import ControladorClimatico
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

app = Flask(__name__)

# Configuración de rangos óptimos
rango_optimo = {
    "temperatura": (18, 30),
    "humedad": (50, 70)
}

# Instancias del controlador y los sensores
controlador = ControladorClimatico(rango_optimo)
sensor_temperatura = Sensor("temperatura", "°C")
sensor_humedad = Sensor("humedad", "%")

controlador.agregar_sensor(sensor_temperatura)
controlador.agregar_sensor(sensor_humedad)


@app.route('/')
def index():
    controlador.tomar_lecturas()
    lecturas = controlador.obtener_lecturas()
    return render_template('index.html', lecturas=lecturas)


@app.route('/alertas')
def alertas():
    alertas = controlador.obtener_alertas()
    return render_template('alertas.html', alertas=alertas)


@app.route('/graficas')
def graficas():
    controlador.tomar_lecturas()
    lecturas = controlador.obtener_lecturas()

    fig, ax = plt.subplots(2, 1, figsize=(10, 8))

    fechas_temp = [fecha for fecha, _ in lecturas['temperatura']]
    valores_temp = [valor for _, valor in lecturas['temperatura']]
    ax[0].plot(fechas_temp, valores_temp,
               label='Temperatura (°C)', color='tab:red')
    ax[0].set_title('Lecturas de Temperatura')
    ax[0].set_xlabel('Fecha')
    ax[0].set_ylabel('Temperatura (°C)')
    ax[0].legend()
    ax[0].grid()

    fechas_hum = [fecha for fecha, _ in lecturas['humedad']]
    valores_hum = [valor for _, valor in lecturas['humedad']]
    ax[1].plot(fechas_hum, valores_hum, label='Humedad (%)', color='tab:blue')
    ax[1].set_title('Lecturas de Humedad')
    ax[1].set_xlabel('Fecha')
    ax[1].set_ylabel('Humedad (%)')
    ax[1].legend()
    ax[1].grid()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close(fig)

    return render_template('graficas.html', plot_url=plot_url)


@app.route('/cargar_archivo', methods=['GET', 'POST'])
def cargar_archivo():
    datos = []

    if request.method == 'POST':
        archivo = request.files['archivo']
        if archivo:
            filename = archivo.filename
            if filename.endswith('.json'):
                datos = leer_json(archivo)
            elif filename.endswith('.csv'):
                datos = leer_csv(archivo)
            else:
                return "Formato de archivo no soportado. Usa JSON o CSV.", 400

    return render_template('cargar_archivo.html', datos=datos)


@app.route('/enviar_correo', methods=['GET', 'POST'])
def enviar_correo():
    mensaje = None

    if request.method == 'POST':
        correo = request.form['correo']
        if correo:
            try:
                # Generar el archivo con los últimos datos
                archivo_path = generar_archivo_lecturas()

                # Enviar el correo
                enviar_email_con_archivo(correo, archivo_path)
                mensaje = "Correo enviado exitosamente."
            except Exception as e:
                mensaje = f"Ocurrió un error al enviar el correo: {e}"

    return render_template('enviar_correo.html', mensaje=mensaje)


def generar_archivo_lecturas():
    """Genera un archivo CSV con las últimas lecturas de temperatura y humedad."""
    lecturas = controlador.obtener_lecturas()
    datos = []

    for tipo, lista in lecturas.items():
        for fecha, valor in lista:
            datos.append({'fecha': fecha.strftime(
                '%Y-%m-%d %H:%M:%S'), 'tipo': tipo, 'valor': valor})

    # Generar un nombre de archivo simple
    archivo_path = os.path.join(os.getcwd(), 'ultimas_lecturas.csv')
    df = pd.DataFrame(datos)
    df.to_csv(archivo_path, index=False)
    return archivo_path


def enviar_email_con_archivo(correo, archivo_path):
    """Envía un correo con un archivo adjunto."""
    remitente = "temperaturassas@gmail.com"  # Cambia esto a tu correo
    contrasena = "zhpq eetu tgii hgqa"       # Usa aquí una contraseña de aplicación
    asunto = "Últimos Datos de Temperatura y Humedad"

    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = correo
    msg['Subject'] = asunto

    # Agregar el cuerpo del mensaje (asegurar UTF-8)
    cuerpo = "Adjunto encontrarás el archivo con las últimas lecturas de temperatura y humedad en un archivo cvs."
    msg.attach(MIMEText(cuerpo.encode('utf-8'), 'plain', 'utf-8'))

    # Adjuntar el archivo
    with open(archivo_path, 'rb') as archivo:
        parte = MIMEBase('application', 'octet-stream')
        parte.set_payload(archivo.read())
        encoders.encode_base64(parte)
        parte.add_header(
            'Content-Disposition',
            f'attachment; filename="{os.path.basename(archivo_path)}"'
        )
        msg.attach(parte)

    # Enviar el correo
    with smtplib.SMTP('smtp.gmail.com', 587) as servidor:
        servidor.starttls()
        servidor.login(remitente, contrasena)
        servidor.send_message(msg)


@app.route('/estadisticas')
def estadisticas():
    # Obtener lecturas actuales
    lecturas = controlador.obtener_lecturas()
    datos = []

    # Transformar lecturas a una lista estructurada
    for tipo, lista in lecturas.items():
        for fecha, valor in lista:
            datos.append({'fecha': fecha, 'tipo': tipo, 'valor': valor})

    # Convertir a DataFrame para estadísticas
    df = pd.DataFrame(datos)

    # Si no hay datos, mostrar mensaje
    if df.empty:
        stats = {"mensaje": "No hay datos suficientes para generar estadísticas."}
    else:
        # Calcular estadísticas
        stats = {
            'temperatura': {
                'promedio': df[df['tipo'] == 'temperatura']['valor'].mean(),
                'maxima': df[df['tipo'] == 'temperatura']['valor'].max(),
                'minima': df[df['tipo'] == 'temperatura']['valor'].min()
            },
            'humedad': {
                'promedio': df[df['tipo'] == 'humedad']['valor'].mean(),
                'maxima': df[df['tipo'] == 'humedad']['valor'].max(),
                'minima': df[df['tipo'] == 'humedad']['valor'].min()
            },
            'criticos': {
                'temperatura': len(df[(df['tipo'] == 'temperatura') & ((df['valor'] < 18) | (df['valor'] > 30))]),
                'humedad': len(df[(df['tipo'] == 'humedad') & ((df['valor'] < 50) | (df['valor'] > 70))])
            }
        }

    # Renderizar la página de estadísticas
    return render_template('estadisticas.html', stats=stats)


def leer_json(archivo):
    # Lee y procesa el archivo JSON
    contenido = json.load(archivo)
    datos = []

    for entrada in contenido:
        fecha = datetime.strptime(entrada['fecha'], '%Y-%m-%d %H:%M:%S')
        temperatura = entrada.get('temperatura')
        humedad = entrada.get('humedad')
        datos.append(
            {'fecha': fecha, 'temperatura': temperatura, 'humedad': humedad})

    return datos


def leer_csv(archivo):
    # Lee y procesa el archivo CSV
    df = pd.read_csv(archivo)
    datos = []

    for _, row in df.iterrows():
        fecha = datetime.strptime(row['fecha'], '%Y-%m-%d %H:%M:%S')
        temperatura = row['temperatura']
        humedad = row['humedad']
        datos.append(
            {'fecha': fecha, 'temperatura': temperatura, 'humedad': humedad})

    return datos


if __name__ == '__main__':
    app.run(debug=True)
