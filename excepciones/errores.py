# Excepción base del dominio: permite capturar cualquier error controlado de Software FJ en un solo tipo.
class ErrorSistemaFJ(Exception):
    def __init__(self, mensaje: str, codigo: str = "ERR-FJ") -> None:
        self.codigo = codigo
        self.mensaje = mensaje
        super().__init__(f"[{codigo}] {mensaje}")


# Se lanza ante entradas inválidas, formatos incorrectos (como correo) o datos faltantes.
class ValidacionDatosError(ErrorSistemaFJ):
    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje, "ERR-VAL")


# Se lanza cuando un servicio no existe o su estado de disponibilidad impide reservarlo.
class ServicioNoDisponibleError(ErrorSistemaFJ):
    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje, "ERR-SRV")


# Se lanza ante transiciones de estado ilegales o reglas de negocio violadas en una reserva.
class OperacionReservaError(ErrorSistemaFJ):
    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje, "ERR-RES")


# Se lanza cuando parámetros numéricos (tarifas, duraciones, descuentos o totales) son inconsistentes.
class CalculoInconsistenteError(ErrorSistemaFJ):
    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje, "ERR-CAL")