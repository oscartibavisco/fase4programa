from abc import ABC, abstractmethod
from modelo.base import EntidadBase
from excepciones.errores import ValidacionDatosError, CalculoInconsistenteError


# Clase abstracta Servicio: aplica patrón plantilla delegando validación y subtotal a las subclases.
class Servicio(EntidadBase, ABC):
    def __init__(self, id_servicio: str, nombre: str, tarifa_hora: float, disponible: bool = True) -> None:
        try:
            super().__init__(id_servicio)
        except ValueError as exc:
            raise ValidacionDatosError("ID de servicio inválido.") from exc

        if not nombre or not nombre.strip():
            raise ValidacionDatosError("El nombre del servicio es obligatorio.")
        if tarifa_hora <= 0:
            raise CalculoInconsistenteError("La tarifa por hora debe ser mayor que cero.")

        self._nombre = nombre.strip()
        self._tarifa_hora = float(tarifa_hora)
        self._disponible = bool(disponible)

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_hora(self) -> float:
        return self._tarifa_hora

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool) -> None:
        self._disponible = bool(valor)

    # Polimorfismo: cada subclase sobrescribe estos métodos abstractos según su dominio específico.
    @abstractmethod
    def validar_parametros(self, horas: int, **kwargs) -> None:
        pass

    @abstractmethod
    def subtotal_servicio(self, horas: int, **kwargs) -> float:
        pass

    # Sobrecarga por argumentos opcionales y **kwargs: admite llamadas con horas mínimas o con impuesto/descuento/ajuste.
    def calcular_costo(
        self,
        horas: int,
        impuesto: float = 0.19,
        descuento: float = 0.0,
        ajuste_tarifa: float | str = 0.0,
        **kwargs,
    ) -> float:
        if not isinstance(horas, int) or horas <= 0:
            raise CalculoInconsistenteError("Las horas deben ser un entero positivo.")
        if not (0.0 <= descuento < 100.0):
            raise CalculoInconsistenteError("El descuento debe estar entre 0 y 99.9.")
        if impuesto < 0:
            raise CalculoInconsistenteError("El impuesto no puede ser negativo.")

        self.validar_parametros(horas, **kwargs)

        tarifa_efectiva = self._aplicar_ajuste(ajuste_tarifa)
        base = self.subtotal_servicio(horas, tarifa_override=tarifa_efectiva, **kwargs)
        con_descuento = base * (1 - descuento / 100.0)
        total = round(con_descuento * (1 + impuesto), 2)

        if total <= 0:
            raise CalculoInconsistenteError("El total calculado no es válido.")
        return total

    # Sobrecarga de comportamiento según tipo de dato (int/float para monto o str porcentual tipo "10%").
    def _aplicar_ajuste(self, ajuste: float | str) -> float:
        if isinstance(ajuste, (int, float)):
            nueva = self._tarifa_hora + float(ajuste)
        elif isinstance(ajuste, str) and ajuste.strip().endswith("%"):
            try:
                pct = float(ajuste.strip()[:-1])
            except ValueError as exc:
                raise CalculoInconsistenteError(f"Porcentaje inválido: '{ajuste}'.") from exc
            nueva = self._tarifa_hora * (1 + pct / 100.0)
        else:
            raise ValidacionDatosError(f"Ajuste de tarifa no soportado: '{ajuste}'.")

        if nueva <= 0:
            raise CalculoInconsistenteError("La tarifa ajustada debe ser mayor que cero.")
        return round(nueva, 2)

    @abstractmethod
    def describir(self) -> str:
        pass


# Subclase especializada para salas: valida aforo máximo y aplica recargo si excede el 50% de capacidad.
class ReservaSala(Servicio):
    def __init__(self, id_servicio: str, nombre: str, tarifa_hora: float, capacidad: int, disponible: bool = True):
        super().__init__(id_servicio, nombre, tarifa_hora, disponible)
        if capacidad <= 0:
            raise ValidacionDatosError("La capacidad de la sala debe ser mayor a 0.")
        self._capacidad = capacidad

    def validar_parametros(self, horas: int, asistentes: int = 1, **kwargs) -> None:
        if asistentes <= 0 or asistentes > self._capacidad:
            raise ValidacionDatosError(f"Asistentes ({asistentes}) fuera de capacidad (1-{self._capacidad}).")

    def subtotal_servicio(self, horas: int, asistentes: int = 1, tarifa_override: float | None = None, **kwargs) -> float:
        tarifa = tarifa_override if tarifa_override is not None else self._tarifa_hora
        extra = 1.15 if asistentes > self._capacidad / 2 else 1.0
        return tarifa * horas * extra

    def describir(self) -> str:
        disp = "Disponible" if self._disponible else "No disponible"
        return f"Sala [{self.id}] {self._nombre} (Cap. {self._capacidad}) - ${self._tarifa_hora:,.2f}/h [{disp}]"


# Subclase especializada para alquiler de equipos: verifica disponibilidad de stock y calcula costo por unidad/hora.
class AlquilerEquipo(Servicio):
    def __init__(self, id_servicio: str, nombre: str, tarifa_hora: float, stock: int, disponible: bool = True):
        super().__init__(id_servicio, nombre, tarifa_hora, disponible)
        if stock < 0:
            raise ValidacionDatosError("El stock no puede ser negativo.")
        self._stock = stock

    def validar_parametros(self, horas: int, cantidad: int = 1, **kwargs) -> None:
        if cantidad <= 0 or cantidad > self._stock:
            raise ValidacionDatosError(f"Cantidad ({cantidad}) sin stock suficiente ({self._stock}).")

    def subtotal_servicio(self, horas: int, cantidad: int = 1, tarifa_override: float | None = None, **kwargs) -> float:
        tarifa = tarifa_override if tarifa_override is not None else self._tarifa_hora
        return tarifa * horas * cantidad

    def describir(self) -> str:
        disp = "Disponible" if self._disponible else "No disponible"
        return f"Equipo [{self.id}] {self._nombre} (Stock {self._stock}) - ${self._tarifa_hora:,.2f}/h [{disp}]"


# Subclase especializada para asesorías: valida rango horario y pondera tarifa según nivel de seniority.
class AsesoriaEspecializada(Servicio):
    def __init__(self, id_servicio: str, nombre: str, tarifa_hora: float, seniority: str = "Senior", disponible: bool = True):
        super().__init__(id_servicio, nombre, tarifa_hora, disponible)
        if seniority.strip().lower() not in {"junior", "semi", "senior"}:
            raise ValidacionDatosError("Seniority inválido (usa Junior, Semi o Senior).")
        self._seniority = seniority.strip().capitalize()

    def validar_parametros(self, horas: int, **kwargs) -> None:
        if horas < 1 or horas > 12:
            raise ValidacionDatosError("La asesoría debe durar entre 1 y 12 horas.")

    def subtotal_servicio(self, horas: int, tarifa_override: float | None = None, **kwargs) -> float:
        tarifa = tarifa_override if tarifa_override is not None else self._tarifa_hora
        mult = 1.25 if self._seniority == "Senior" else 1.0
        return tarifa * horas * mult

    def describir(self) -> str:
        disp = "Disponible" if self._disponible else "No disponible"
        return f"Asesoría [{self.id}] {self._nombre} ({self._seniority}) - ${self._tarifa_hora:,.2f}/h [{disp}]"