from abc import ABC, abstractmethod
from datetime import datetime

# Clase Abstracta que define la interfaz base para los vehículos
class VehiculoAbstracto(ABC):
    @abstractmethod
    def obtener_placa(self) -> str:
        pass

    @abstractmethod
    def calcular_pago(self, hora_salida: datetime) -> float:
        pass

# Clase Auto que implementa la abstracción y el encapsulamiento
class Auto(VehiculoAbstracto):
    def __init__(self, placa: str, tarifa_hora: float):
        self._placa = placa                # Atributo privado/protegido
        self._hora_ingreso = None          # Atributo privado/protegido
        self._tarifa_hora = tarifa_hora    # Atributo privado/protegido
        self._hora_salida = None

    def registrar_ingreso(self, hora: datetime) -> None:
        self._hora_ingreso = hora

    def registrar_salida(self, hora: datetime) -> None:
        if hora < self._hora_ingreso:
            raise ValueError("La hora de salida no puede ser anterior a la hora de ingreso.")
        self._hora_salida = hora

    def calcular_pago(self, hora_salida: datetime) -> float:
        self.registrar_salida(hora_salida)
        
        # Calcular el tiempo transcurrido en horas
        diferencia = self._hora_salida - self._hora_ingreso
        horas_transcurridas = diferencia.total_seconds() / 3600
        
        # Cobro mínimo de 1 hora si el tiempo es menor, o fracción exacta
        horas_cobro = max(1.0, horas_transcurridas)
        return round(horas_cobro * self._tarifa_hora, 2)

    def obtener_placa(self) -> str:
        return self._placa

    @property
    def hora_ingreso(self) -> datetime:
        return self._hora_ingreso

# Clase AutoLavado que gestiona la lista interna de vehículos
class AutoLavado:
    def __init__(self, nombre: str):
        self._nombre = nombre
        self._vehiculos_en_proceso = []  # Lista interna para almacenar los autos

    def registrar_ingreso_auto(self, placa: str, tarifa_hora: float, hora_ingreso: datetime) -> None:
        # Verificar si ya existe un auto con la misma placa
        if any(auto.obtener_placa().upper() == placa.upper() for auto in self._vehiculos_en_proceso):
            print(f"El auto con placa {placa} ya se encuentra registrado en el autolavado.")
            return

        nuevo_auto = Auto(placa, tarifa_hora)
        nuevo_auto.registrar_ingreso(hora_ingreso)
        self._vehiculos_en_proceso.append(nuevo_auto)
        print(f"Éxito: Auto con placa [{placa.upper()}] ingresado a las {hora_ingreso.strftime('%H:%M')}.")

    def _buscar_auto(self, placa: str) -> Auto:
        for auto in self._vehiculos_en_proceso:
            if auto.obtener_placa().upper() == placa.upper():
                return auto
        return None

    def procesar_salida(self, placa: str, hora_salida: datetime) -> None:
        auto = self._buscar_auto(placa)
        
        if not auto:
            print(f"Error: No se encontró ningún vehículo activo con la placa {placa}.")
            return

        try:
            # Validación y cálculo automático del costo
            costo_total = auto.calcular_pago(hora_salida)
            
            # Remover de la lista interna al salir
            self._vehiculos_en_proceso.remove(auto)
            
            print("\n--- TICKET DE SALIDA ---")
            print(f"Placa: {auto.obtener_placa()}")
            print(f"Ingreso: {auto.hora_ingreso.strftime('%H:%M')}")
            print(f"Salida: {hora_salida.strftime('%H:%M')}")
            print(f"Total a Pagar: ${costo_total:.2f}")
            print("------------------------\n")
            
        except ValueError as e:
            print(f"Error de validación en la salida: {e}")

    def listar_autos_activos(self) -> None:
        if not self._vehiculos_en_proceso:
            print("No hay autos en proceso de lavado actualmente.")
            return
        
        print("\n--- AUTOS EN PROCESO ---")
        for auto in self._vehiculos_en_proceso:
            print(f"Placa: {auto.obtener_placa()} | Ingreso: {auto.hora_ingreso.strftime('%H:%M')}")
        print("------------------------\n")

# --- Ejemplo de uso ---
if __name__ == "__main__":
    lavado = AutoLavado("EcoWash")

    # Registrar ingresos
    lavado.registrar_ingreso_auto("ABC-123", tarifa_hora=15.0, hora_ingreso=datetime(2026, 6, 6, 10, 0))
    lavado.registrar_ingreso_auto("XYZ-789", tarifa_hora=20.0, hora_ingreso=datetime(2026, 6, 6, 10, 30))

    # Ver lista de autos activos
    lavado.listar_autos_activos()

    # Intentar registrar salida con hora inválida (anterior al ingreso)
    lavado.procesar_salida("ABC-123", datetime(2026, 6, 6, 9, 30))

    # Registrar salida correcta (ej. a las 12:00 -> 2 horas transcurridas)
    lavado.procesar_salida("ABC-123", datetime(2026, 6, 6, 12, 0))

    # Verificar lista después de la salida
    lavado.listar_autos_activos()