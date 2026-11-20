import re
from modelo.base import EntidadBase
from excepciones.errores import ValidacionDatosError


class Cliente(EntidadBase):
    def __init__(self, id_cliente: str, nombre: str, correo: str, activo: bool = True) -> None:
        try:
            super().__init__(id_cliente)
        except ValueError as exc:
            raise ValidacionDatosError("ID de cliente inválido.") from exc

        self.nombre = nombre
        self.correo = correo
        self._activo = bool(activo)

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or len(valor.strip()) < 2:
            raise ValidacionDatosError("Nombre de cliente muy corto.")
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        if not isinstance(valor, str) or not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", valor.strip()):
            raise ValidacionDatosError(f"Correo inválido: '{valor}'.")
        self._correo = valor.strip().lower()

    @property
    def activo(self) -> bool:
        return self._activo

    def desactivar(self) -> None:
        self._activo = False

    def describir(self) -> str:
        estado = "Activo" if self._activo else "Inactivo"
        return f"Cliente [{self.id}] {self._nombre} ({self._correo}) - {estado}"