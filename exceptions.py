class AirportOperationsError(Exception):
    """Excepción base para todos los errores del sistema AirNode."""
    def __init__(self, message: str, code: int = 500):
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self):
        return f"[Error {self.code}] {self.message}"


class GateCapacityExceededError(AirportOperationsError):
    """Se dispara cuando una terminal se queda sin puertas disponibles."""
    def __init__(self, terminal_name: str, flight_id: str):
        message = f"Terminal '{terminal_name}' llena. Imposible asignar puerta al vuelo '{flight_id}'."
        super().__init__(message, code=401)


class RunwayOccupiedError(AirportOperationsError):
    """Se dispara si hay un conflicto de horarios en pista."""
    def __init__(self, runway_id: str, timestamp: str):
        message = f"Pista '{runway_id}' ocupada en la franja horaria: {timestamp}."
        super().__init__(message, code=402)


class InvalidScheduleFormatError(AirportOperationsError):
    """Error al procesar la estructura de un archivo de vuelos."""
    def __init__(self, file_path: str, line_num: int):
        message = f"Formato inválido en '{file_path}' (Línea {line_num} por favor)."
        super().__init__(message, code=403)
