from sensor import Sensor
from controlador import ControladorClimatico

sensor_temperatura = Sensor("temperatura", "°C")
sensor_humedad = Sensor("humedad", "%")

controlador = ControladorClimatico({"temperatura": (18, 30), "humedad": (50, 70)})
controlador.agregar_sensor(sensor_temperatura)
controlador.agregar_sensor(sensor_humedad)

# Toma de lecturas y verificación de alertas
controlador.tomar_lecturas()
print(controlador.obtener_lecturas())
print(controlador.obtener_alertas())
