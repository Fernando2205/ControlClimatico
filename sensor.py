# sensor.py
import random
from datetime import datetime

class Sensor:
    def __init__(self, tipo, unidad):
        self.tipo = tipo  # "temperatura" o "humedad"
        self.unidad = unidad  # "°C" para temperatura, "%" para humedad
        self.lecturas = []  # Lista para almacenar las lecturas

    def tomar_lectura(self):
        # Genera una lectura aleatoria según el tipo de sensor
        if self.tipo == "temperatura":
            valor = random.uniform(15, 35)
        elif self.tipo == "humedad":
            valor = random.uniform(40, 80)
        
        # Guarda la lectura junto con la fecha y hora actuales
        self.lecturas.append((datetime.now(), valor))
        return valor

    def obtener_lecturas(self):
        return self.lecturas
