from enum import Enum
from modelo.base import EntidadBase
from modelo.cliente import Cliente
from modelo.servicio import Servicio
from excepciones.errores import (
    ValidacionDatosError,
    ServicioNoDisponibleError,
    OperacionReservaError,
    CalculoInconsistenteError,
)


# Enumeración que define la máquina de estados permitidos en el ciclo de vida de una reserva.
class EstadoReserva(Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    PROCESADA = "PROCESADA"


# Agrega Cliente y Servicio, calcula el costo total y protege confirmar(), cancelar() y procesar().
class Reserva(EntidadBase):
    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion_horas: int,
        impuesto: float = 0.19,
        descuento: float = 0.0,
        ajuste_tarifa: float | str = 0.0,
        **kwargs,
    ) -> None:
        try:
            super().__init__(id_reserva)
        except ValueError as exc:
            raise ValidacionDatosError("ID de reserva inválido.") from exc

        if not isinstance(cliente, Cliente):
            raise ValidacionDatosError("Cliente inválido.")
        if not cliente.activo:
            raise OperacionReservaError(f"El cliente '{cliente.nombre}' está inactivo.")

        if not isinstance(servicio, Servicio):
            raise ValidacionDatosError("Servicio inválido.")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no está disponible.")

        self._cliente = cliente
        self._servicio = servicio
        self._duracion_horas = duracion_horas
        self._estado = EstadoReserva.PENDIENTE

        try:
            self._total = self._servicio.calcular_costo(
                horas=duracion_horas,
                impuesto=impuesto,
                descuento=descuento,
                ajuste_tarifa=ajuste_tarifa,
                **kwargs,
            )
        except CalculoInconsistenteError:
            raise
        except ValidacionDatosError as exc:
            # Encadena ValidacionDatosError hacia OperacionReservaError al fallar parámetros de reserva.
            raise OperacionReservaError("Error en parámetros de la reserva.") from exc

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def total(self) -> float:
        return self._total

    def confirmar(self) -> str:
        if self._estado in {EstadoReserva.CANCELADA, EstadoReserva.PROCESADA}:
            raise OperacionReservaError(f"No se puede confirmar [{self.id}] en estado {self._estado.value}.")
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(f"Servicio '{self._servicio.nombre}' no disponible.")
        self._estado = EstadoReserva.CONFIRMADA
        return f"Reserva [{self.id}] CONFIRMADA (${self._total:,.2f})"

    def cancelar(self, motivo: str = "Sin motivo") -> str:
        if self._estado in {EstadoReserva.PROCESADA, EstadoReserva.CANCELADA}:
            raise OperacionReservaError(f"No se puede cancelar [{self.id}] en estado {self._estado.value}.")
        self._estado = EstadoReserva.CANCELADA
        return f"Reserva [{self.id}] CANCELADA - {motivo}"

    def procesar(self) -> str:
        try:
            if self._estado != EstadoReserva.CONFIRMADA:
                raise OperacionReservaError(f"Solo se procesan reservas CONFIRMADAS ([{self.id}]: {self._estado.value}).")
            if self._total <= 0:
                raise CalculoInconsistenteError("Total inválido al procesar.")
        except CalculoInconsistenteError as exc:
            raise OperacionReservaError(f"Fallo al procesar [{self.id}].") from exc

        self._estado = EstadoReserva.PROCESADA
        return f"Reserva [{self.id}] PROCESADA (${self._total:,.2f})"

    def describir(self) -> str:
        return (
            f"Reserva [{self.id}] | {self._cliente.nombre} | {self._servicio.nombre} | "
            f"{self._duracion_horas}h | ${self._total:,.2f} | {self._estado.value}"
        )