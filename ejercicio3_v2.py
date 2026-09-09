from datetime import datetime
import math
import tkinter as tk
from tkinter import messagebox, ttk


class CarWashService:
    """Clase de dominio que representa un vehículo y su servicio en el lavadero.

    Aplica encapsulamiento mediante atributos protegidos y propiedades de
    lectura/escritura.
    """

    def __init__(
        self, license_plate: str, entry_time_str: str, hourly_rate: float
    ):
        """Inicializa los atributos privados del vehículo."""
        self._license_plate = self._validate_plate(license_plate)
        self._entry_time = self._parse_time(entry_time_str)
        self._hourly_rate = self._validate_rate(hourly_rate)
        self._exit_time = None

    @staticmethod
    def _validate_plate(plate: str) -> str:
        """Método privado para validar que la placa no esté vacía."""
        clean_plate = plate.strip().upper()
        if not clean_plate or len(clean_plate) < 6:
            raise ValueError("License plate cannot be empty and must be at least 6 characters long.")
        return clean_plate

    @staticmethod
    def _validate_rate(rate: float) -> float:
        """Método privado para validar que la tarifa sea mayor a cero."""
        if rate <= 0:
            raise ValueError("Hourly rate must be greater than zero.")
        return rate

    @staticmethod
    def _parse_time(time_str: str) -> datetime:
        """Método privado auxiliar para convertir cadenas a formato HH:MM."""
        try:
            return datetime.strptime(time_str.strip(), "%H:%M")
        except ValueError:
            raise ValueError(
                "Invalid time format. Please use HH:MM (24-hour format)."
            )

    @property
    def license_plate(self) -> str:
        """Getter para obtener la placa del vehículo."""
        return self._license_plate

    @property
    def entry_time(self) -> datetime:
        """Getter para obtener la hora de ingreso."""
        return self._entry_time

    @property
    def entry_time_str(self) -> str:
        """Getter para obtener la hora de ingreso en formato texto HH:MM."""
        return self._entry_time.strftime("%H:%M")

    @property
    def hourly_rate(self) -> float:
        """Getter para obtener la tarifa por hora."""
        return self._hourly_rate

    @property
    def exit_time(self) -> datetime:
        """Getter para obtener la hora de salida."""
        return self._exit_time

    def register_entry(self, entry_time_str: str) -> None:
        """Setter/Método para registrar o modificar la hora de ingreso."""
        self._entry_time = self._parse_time(entry_time_str)

    def register_exit(self, exit_time_str: str) -> None:
        """Registra y valida la hora de salida respecto a la de entrada."""
        exit_dt = self._parse_time(exit_time_str)
        if exit_dt < self._entry_time:
            raise ValueError("Exit time cannot be earlier than entry time.")
        self._exit_time = exit_dt

    def calculate_payment(self, exit_time_str: str = None) -> float:
        """Calcula el monto total a pagar.

        Redondea hacia arriba cada hora o fracción transcurrida.
        """
        if exit_time_str:
            self.register_exit(exit_time_str)

        if self._exit_time is None:
            raise ValueError("Exit time has not been registered.")

        duration_seconds = (
            self._exit_time - self._entry_time
        ).total_seconds()
        duration_hours = duration_seconds / 3600.0

        # Cobro mínimo de 1 hora y redondeo hacia arriba por fracción
        billed_hours = max(1, math.ceil(duration_hours))
        return billed_hours * self._hourly_rate


class CarWashManager:
    """Clase administradora que controla la lista interna de servicios activos."""

    def __init__(self):
        """Inicializa la lista interna de vehículos registrados."""
        self._active_vehicles = []

    def add_vehicle(self, vehicle: CarWashService) -> None:
        """Agrega un vehículo validando que no esté previamente registrado."""
        if self.find_vehicle(vehicle.license_plate) is not None:
            raise ValueError(
                f"Vehicle with plate '{vehicle.license_plate}' is already in the car wash."
            )
        self._active_vehicles.append(vehicle)

    def remove_vehicle(self, license_plate: str) -> CarWashService:
        """Remueve un vehículo registrado y lo retorna."""
        vehicle = self.find_vehicle(license_plate)
        if vehicle is None:
            raise ValueError(
                f"Vehicle with plate '{license_plate}' not found."
            )
        self._active_vehicles.remove(vehicle)
        return vehicle

    def find_vehicle(self, license_plate: str) -> CarWashService:
        """Busca un vehículo por su placa dentro de la lista interna."""
        clean_plate = license_plate.strip().upper()
        for vehicle in self._active_vehicles:
            if vehicle.license_plate == clean_plate:
                return vehicle
        return None

    def get_all_vehicles(self) -> list:
        """Retorna una copia de la lista para preservar el encapsulamiento."""
        return list(self._active_vehicles)


class CarWashApp(tk.Tk):
    """Interfaz gráfica principal construida con Tkinter."""

    def __init__(self):
        super().__init__()
        self.title("Car Wash Management System")
        self.geometry("640x520")
        self.resizable(False, False)

        self._manager = CarWashManager()
        self._setup_ui()

    def _setup_ui(self):
        """Configura los elementos de la interfaz gráfica."""
        # Marco para Ingreso de Vehículos
        entry_frame = ttk.LabelFrame(self, text=" Vehicle Registration ")
        entry_frame.pack(fill="x", padx=15, pady=10)

        ttk.Label(entry_frame, text="License Plate:").grid(
            row=0, column=0, padx=5, pady=5
        )
        self.entry_plate = ttk.Entry(entry_frame)
        self.entry_plate.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(entry_frame, text="Check-In Time (HH:MM):").grid(
            row=0, column=2, padx=5, pady=5
        )
        self.entry_in_time = ttk.Entry(entry_frame)
        self.entry_in_time.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(entry_frame, text="Hourly Rate ($):").grid(
            row=1, column=0, padx=5, pady=5
        )
        self.entry_rate = ttk.Entry(entry_frame)
        self.entry_rate.grid(row=1, column=1, padx=5, pady=5)

        btn_checkin = ttk.Button(
            entry_frame, text="Register Entry", command=self._handle_check_in
        )
        btn_checkin.grid(row=1, column=2, columnspan=2, padx=5, pady=5)

        # Tabla de Vehículos Activos
        table_frame = ttk.LabelFrame(self, text=" Active Vehicles ")
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("plate", "entry_time", "rate")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=8
        )
        self.tree.heading("plate", text="License Plate")
        self.tree.heading("entry_time", text="Check-In Time")
        self.tree.heading("rate", text="Rate / Hour ($)")

        self.tree.column("plate", anchor="center", width=180)
        self.tree.column("entry_time", anchor="center", width=180)
        self.tree.column("rate", anchor="center", width=180)

        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self._on_vehicle_selected)

        # Marco para Salida de Vehículos
        exit_frame = ttk.LabelFrame(self, text=" Vehicle Check-Out ")
        exit_frame.pack(fill="x", padx=15, pady=10)

        ttk.Label(exit_frame, text="Selected Plate:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.entry_out_plate = ttk.Entry(exit_frame, state="readonly")
        self.entry_out_plate.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(exit_frame, text="Check-Out Time (HH:MM):").grid(
            row=0, column=2, padx=5, pady=5, sticky="w"
        )
        self.entry_out_time = ttk.Entry(exit_frame)
        self.entry_out_time.grid(row=0, column=3, padx=5, pady=5)

        btn_checkout = ttk.Button(
            exit_frame, text="Process Exit & Pay", command=self._handle_check_out
        )
        btn_checkout.grid(
            row=1, column=0, columnspan=4, padx=5, pady=5
        )

    def _handle_check_in(self):
        """Maneja el evento de registrar un vehículo."""
        plate = self.entry_plate.get()
        time_str = self.entry_in_time.get()
        rate_str = self.entry_rate.get()

        try:
            rate = float(rate_str)
            vehicle = CarWashService(plate, time_str, rate)
            self._manager.add_vehicle(vehicle)
            self._refresh_table()
            self._clear_check_in_entries()
            messagebox.showinfo(
                "Success", f"Vehicle '{vehicle.license_plate}' registered successfully."
            )
        except ValueError as err:
            messagebox.showerror("Error", str(err))

    def _handle_check_out(self):
        """Maneja el evento de registrar la salida de un vehículo."""
        plate = self.entry_out_plate.get()
        exit_time_str = self.entry_out_time.get()

        if not plate:
            messagebox.showwarning(
                "Warning", "Please select a vehicle from the list."
            )
            return

        try:
            vehicle = self._manager.find_vehicle(plate)
            total_cost = vehicle.calculate_payment(exit_time_str)
            self._manager.remove_vehicle(plate)

            self._refresh_table()
            self._clear_check_out_entries()

            messagebox.showinfo(
                "Receipt",
                f"Vehicle: {plate}\n"
                f"Entry Time: {vehicle.entry_time_str}\n"
                f"Exit Time: {exit_time_str}\n"
                f"Total Due: ${total_cost:.2f}",
            )
        except ValueError as err:
            messagebox.showerror("Error", str(err))

    def _on_vehicle_selected(self, event):
        """Rena el campo de salida al seleccionar un elemento de la lista."""
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item[0], "values")
            self.entry_out_plate.config(state="normal")
            self.entry_out_plate.delete(0, tk.END)
            self.entry_out_plate.insert(0, values[0])
            self.entry_out_plate.config(state="readonly")

    def _refresh_table(self):
        """Actualiza la tabla con los datos actuales del manager."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        for v in self._manager.get_all_vehicles():
            self.tree.insert(
                "", tk.END, values=(v.license_plate, v.entry_time_str, f"{v.hourly_rate:.2f}")
            )

    def _clear_check_in_entries(self):
        """Limpia los inputs de registro de entrada."""
        self.entry_plate.delete(0, tk.END)
        self.entry_in_time.delete(0, tk.END)
        self.entry_rate.delete(0, tk.END)

    def _clear_check_out_entries(self):
        """Limpia los inputs de registro de salida."""
        self.entry_out_plate.config(state="normal")
        self.entry_out_plate.delete(0, tk.END)
        self.entry_out_plate.config(state="readonly")
        self.entry_out_time.delete(0, tk.END)


if __name__ == "__main__":
    app = CarWashApp()
    app.mainloop()