from abc import ABC, abstractmethod
from datetime import datetime


# Abstracción: clase base ABC que define atributos comunes y exige implementar describir() en subclases.
class EntidadBase(ABC):
    def __init__(self, id_entidad: str) -> None:
        if not isinstance(id_entidad, str) or not id_entidad.strip():
            raise ValueError("El ID no puede estar vacío.")
        # Encapsulación: atributos protegidos (_id, _creado_en) expuestos de solo lectura mediante @property.
        self._id = id_entidad.strip().upper()
        self._creado_en = datetime.now()

    @property
    def id(self) -> str:
        return self._id

    @property
    def creado_en(self) -> datetime:
        return self._creado_en

    @abstractmethod
    def describir(self) -> str:
        pass