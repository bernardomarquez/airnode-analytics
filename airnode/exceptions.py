class AirportOperationsError(Exception):
    """Base exception for all AirNode system errors."""
    def __init__(self, message: str, code: int = 500):
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self):
        return f"[Error {self.code}] {self.message}"


class GateCapacityExceededError(AirportOperationsError):
    """Raised when a terminal runs out of available gates."""
    def __init__(self, terminal_name: str, flight_id: str):
        message = f"Terminal '{terminal_name}' is full. Unable to assign gate for flight '{flight_id}'."
        super().__init__(message, code=401)


class RunwayOccupiedError(AirportOperationsError):
    """Raised if there is a scheduling conflict on a runway."""
    def __init__(self, runway_id: str, timestamp: str):
        message = f"Runway '{runway_id}' is occupied at time slot: {timestamp}."
        super().__init__(message, code=402)


class InvalidScheduleFormatError(AirportOperationsError):
    """Raised when processing an invalid flight schedule file structure."""
    def __init__(self, file_path: str, line_num: int):
        message = f"Invalid format in '{file_path}' at line {line_num}."
        super().__init__(message, code=403)
