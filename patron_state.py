class ReservaState:
    def confirmar(self, reserva):
        pass
    
    def cancelar(self, reserva):
        pass
    
    def finalizar(self, reserva):
        pass


class Pendiente(ReservaState):
    def confirmar(self, reserva):
        print("Reserva confirmada.")
        reserva.state = Confirmada()

    def cancelar(self, reserva):
        print("Reserva cancelada.")
        reserva.state = Cancelada()


class Confirmada(ReservaState):
    def finalizar(self, reserva):
        print("Reserva finalizada.")
        reserva.state = Finalizada()

    def cancelar(self, reserva):
        print("No se puede cancelar una reserva confirmada directamente.")
    

class Cancelada(ReservaState):
    pass


class Finalizada(ReservaState):
    pass


class Reserva:
    def __init__(self):
        self.state = Pendiente()

    def confirmar(self):
        self.state.confirmar(self)

    def cancelar(self):
        self.state.cancelar(self)

    def finalizar(self):
        self.state.finalizar(self)


# Uso del sistema de estados
reserva = Reserva()
reserva.confirmar()  # Reserva confirmada
reserva.finalizar()  # Reserva finalizada
reserva.cancelar()   # No se puede cancelar una reserva finalizada