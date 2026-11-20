# Expone la jerarquía de excepciones del dominio para importarlas de forma centralizada.
from excepciones.errores import (
    ErrorSistemaFJ,
    ValidacionDatosError,
    ServicioNoDisponibleError,
    OperacionReservaError,
    CalculoInconsistenteError,
)