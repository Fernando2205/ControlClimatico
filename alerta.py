# alerta.py
class Alerta:
    def __init__(self, sensor_tipo, valor, fecha):
        self.sensor_tipo = sensor_tipo  # Tipo de sensor: temperatura o humedad
        self.valor = valor  # Valor de la lectura que generó la alerta
        self.fecha = fecha  # Fecha y hora de la alerta

    def __str__(self):
        return f"Alerta en {self.sensor_tipo} - Valor {self.valor} en {self.fecha}"
