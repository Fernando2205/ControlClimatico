from alerta import Alerta


class ControladorClimatico:
    def __init__(self, rango_optimo):
        self.sensores = []  # Lista de sensores
        self.rango_optimo = rango_optimo  # Diccionario con rangos óptimos
        self.alertas = []  # Lista para almacenar alertas

    def agregar_sensor(self, sensor):
        self.sensores.append(sensor)

    def tomar_lecturas(self):
        for sensor in self.sensores:
            valor = sensor.tomar_lectura()
            # Verifica si la lectura está fuera del rango óptimo
            if not (self.rango_optimo[sensor.tipo][0] <= valor <= self.rango_optimo[sensor.tipo][1]):
                # Crea una alerta si el valor está fuera del rango
                alerta = Alerta(sensor.tipo, valor, sensor.lecturas[-1][0])
                self.alertas.append(alerta)

    def obtener_alertas(self):
        return self.alertas

    # controlador.py
    def obtener_lecturas(self):
        return {sensor.tipo: sensor.obtener_lecturas() for sensor in self.sensores}
