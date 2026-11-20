import logging
from pathlib import Path
from modelo.cliente import Cliente
from modelo.servicio import Servicio
from modelo.reserva import Reserva
from excepciones.errores import (
    ErrorSistemaFJ,
    ValidacionDatosError,
    ServicioNoDisponibleError,
    OperacionReservaError,
)


# Configura el archivo de logs para registrar eventos y errores sin usar bases de datos[cite: 1, 2, 3].
def crear_logger(ruta: str = "logs/sistema_fj.log") -> logging.Logger:
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        fh = logging.FileHandler(ruta, mode="a", encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(fh)
    return logger


# Mantiene todo en listas internas en memoria y aplica distintos patrones de manejo de excepciones[cite: 1, 2, 3].
class GestorSistemaFJ:
    def __init__(self, ruta_log: str = "logs/sistema_fj.log") -> None:
        self.logger = crear_logger(ruta_log)
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []
        self._total_ops = 0

    # Valida parámetros obligatorios antes de registrar un cliente (cubre parámetros faltantes/vacíos)[cite: 2, 29].
    def agregar_cliente(self, cliente: Cliente | None) -> str:
        if cliente is None:
            raise ValidacionDatosError("Falta el objeto Cliente (parámetro obligatorio).")
        if any(c.id == cliente.id for c in self.clientes):
            raise ValidacionDatosError(f"Cliente duplicado: {cliente.id}")
        self.clientes.append(cliente)
        return cliente.describir()

    def agregar_servicio(self, servicio: Servicio | None) -> str:
        if servicio is None:
            raise ServicioNoDisponibleError("Falta el objeto Servicio (parámetro obligatorio).")
        if any(s.id == servicio.id for s in self.servicios):
            raise ValidacionDatosError(f"Servicio duplicado: {servicio.id}")
        self.servicios.append(servicio)
        return servicio.describir()

    def buscar_cliente(self, id_cliente: str) -> Cliente:
        if not isinstance(id_cliente, str) or not id_cliente.strip():
            raise ValidacionDatosError("Falta el ID del cliente para realizar la búsqueda.")
        try:
            c = next((x for x in self.clientes if x.id == id_cliente.strip().upper()), None)
            if not c:
                raise KeyError(id_cliente)
            return c
        except KeyError as exc:
            # Encadena KeyError hacia ValidacionDatosError preservando la causa original[cite: 2, 29].
            raise ValidacionDatosError(f"Cliente '{id_cliente}' no encontrado.") from exc

    def buscar_servicio(self, id_servicio: str) -> Servicio:
        if not isinstance(id_servicio, str) or not id_servicio.strip():
            raise ServicioNoDisponibleError("Falta el ID del servicio para realizar la búsqueda.")
        try:
            s = next((x for x in self.servicios if x.id == id_servicio.strip().upper()), None)
            if not s:
                raise KeyError(id_servicio)
            return s
        except KeyError as exc:
            raise ServicioNoDisponibleError(f"Servicio '{id_servicio}' no encontrado.") from exc

    def buscar_reserva(self, id_reserva: str) -> Reserva:
        if not isinstance(id_reserva, str) or not id_reserva.strip():
            raise OperacionReservaError("Falta el ID de la reserva para realizar la búsqueda.")
        try:
            r = next((x for x in self.reservas if x.id == id_reserva.strip().upper()), None)
            if not r:
                raise KeyError(id_reserva)
            return r
        except KeyError as exc:
            raise OperacionReservaError(f"Reserva '{id_reserva}' no encontrada.") from exc

    def crear_reserva(self, id_reserva: str, id_cliente: str, id_servicio: str, horas: int, **kwargs) -> str:
        if not id_reserva or not str(id_reserva).strip():
            raise OperacionReservaError("Falta el ID de la reserva.")
        cliente = self.buscar_cliente(id_cliente)
        servicio = self.buscar_servicio(id_servicio)
        reserva = Reserva(id_reserva, cliente, servicio, horas, **kwargs)
        self.reservas.append(reserva)
        return reserva.describir()

    # Bloque try / except / else: registra el resultado exitoso solo cuando no hubo excepciones[cite: 2, 29].
    def _registrar_resultado(self, n: int, nombre_op: str, fn):
        try:
            res = fn()
        except ErrorSistemaFJ as err:
            causa = f" (Causa: {err.__cause__})" if err.__cause__ else ""
            self.logger.error(f"Op {n} [{nombre_op}] -> {err}{causa}")
            print(f"[ERROR] Op {n} - {nombre_op}: {err}")
            return None
        except Exception as err:
            self.logger.critical(f"Op {n} [{nombre_op}] -> Inesperado: {err}")
            print(f"[CRÍTICO] Op {n} - {nombre_op}: {err}")
            return None
        else:
            self.logger.info(f"Op {n} [{nombre_op}] -> OK: {res}")
            print(f"[OK] Op {n} - {nombre_op}: {res}")
            return res

    # Bloque try / except / finally: garantiza contabilizar y cerrar la traza aunque ocurra un fallo[cite: 2, 29].
    def correr_op(self, n: int, nombre_op: str, fn):
        self._total_ops += 1
        try:
            return self._registrar_resultado(n, nombre_op, fn)
        except Exception as err:
            self.logger.critical(f"Fallo externo en Op {n} [{nombre_op}]: {err}")
            return None
        finally:
            self.logger.info(f"Fin Op {n} [{nombre_op}] (Acumulado ops: {self._total_ops})")