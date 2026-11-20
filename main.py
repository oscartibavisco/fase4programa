from modelo.cliente import Cliente
from modelo.servicio import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from gestores.gestor_sistema import GestorSistemaFJ


# Ejecuta 13 operaciones (válidas e inválidas) en memoria para validar estabilidad y logs[cite: 2, 3, 29, 30].
def main() -> None:
    app = GestorSistemaFJ("logs/sistema_fj.log")
    app.logger.info("--- Inicio simulación Software FJ ---")

    # 1. Cliente válido
    app.correr_op(1, "Cliente válido CLI-01", lambda: app.agregar_cliente(Cliente("CLI-01", "Laura Gómez", "laura@fj.co")))

    # 2. Cliente inválido (correo mal formado)
    app.correr_op(2, "Cliente inválido CLI-02", lambda: app.agregar_cliente(Cliente("CLI-02", "Carlos Ruiz", "correo_malo")))

    # 3. Parámetro faltante al intentar registrar un cliente vacío/nulo[cite: 2, 29]
    app.correr_op(3, "Cliente faltante (None)", lambda: app.agregar_cliente(None))

    # 4. Segundo cliente válido
    app.correr_op(4, "Cliente válido CLI-03", lambda: app.agregar_cliente(Cliente("CLI-03", "Andrés Pardo", "andres@fj.co")))

    # 5. Crear los 3 servicios especializados[cite: 2, 29]
    def cargar_servicios():
        app.agregar_servicio(ReservaSala("SALA-1", "Sala Reuniones", 80000, capacidad=10))
        app.agregar_servicio(AlquilerEquipo("EQ-1", "Portátil Pro", 25000, stock=5))
        app.agregar_servicio(AsesoriaEspecializada("ASE-1", "Soporte Cloud", 120000, seniority="Senior"))
        return "Servicios registrados"

    app.correr_op(5, "Crear servicios", cargar_servicios)

    # 6. Servicio inválido (tarifa negativa -> CalculoInconsistenteError)[cite: 2, 29]
    app.correr_op(6, "Servicio tarifa negativa", lambda: app.agregar_servicio(ReservaSala("SALA-ERR", "Sala Error", -10000, capacidad=5)))

    # 7. Reserva exitosa con descuento y confirmación[cite: 2, 29]
    def res_y_conf():
        app.crear_reserva("RES-1", "CLI-01", "SALA-1", 3, descuento=10.0, asistentes=7)
        return app.buscar_reserva("RES-1").confirmar()

    app.correr_op(7, "Crear y confirmar RES-1", res_y_conf)

    # 8. Procesar reserva confirmada[cite: 2, 29]
    app.correr_op(8, "Procesar RES-1", lambda: app.buscar_reserva("RES-1").procesar())

    # 9. Reserva fallida por exceder capacidad de sala[cite: 2, 29]
    app.correr_op(9, "Exceso capacidad en sala", lambda: app.crear_reserva("RES-2", "CLI-03", "SALA-1", 2, asistentes=20))

    # 10. Reserva exitosa de equipo[cite: 2, 29]
    app.correr_op(10, "Alquiler equipo RES-3", lambda: app.crear_reserva("RES-3", "CLI-03", "EQ-1", 4, cantidad=2))

    # 11. Reserva fallida por servicio no disponible[cite: 2, 29]
    def srv_no_disp():
        s = app.buscar_servicio("ASE-1")
        s.disponible = False
        return app.crear_reserva("RES-4", "CLI-01", "ASE-1", 2)

    app.correr_op(11, "Servicio no disponible", srv_no_disp)

    # 12. Operación no permitida: cancelar reserva ya procesada[cite: 2, 29]
    app.correr_op(12, "Cancelar RES-1 ya procesada", lambda: app.buscar_reserva("RES-1").cancelar("Tarde"))

    # 13. Cancelar reserva pendiente y calcular costo con ajuste porcentual[cite: 2, 29]
    def cancelar_y_ajustar():
        msg = app.buscar_reserva("RES-3").cancelar("Reprogramación")
        total_nuevo = app.buscar_servicio("EQ-1").calcular_costo(2, cantidad=1, ajuste_tarifa="10%")
        return f"{msg} | Cotización 2h con +10% tarifa: ${total_nuevo:,.2f}"

    app.correr_op(13, "Cancelar RES-3 y cotizar con ajuste", cancelar_y_ajustar)

    print(f"\nTotal -> Clientes: {len(app.clientes)} | Servicios: {len(app.servicios)} | Reservas: {len(app.reservas)}")
    app.logger.info("--- Fin simulación Software FJ ---")


if __name__ == "__main__":
    main()
    input("\nPresiona Enter para cerrar la consola...")