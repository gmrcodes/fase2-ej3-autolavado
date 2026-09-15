import math
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk, font

SYSTEM_FONT = "TkDefaultFont"

class User:
    """Representa el usuario del sistema de autenticación."""

    def __init__(self, username="123", password="123"):
        """Inicializa el usuario con validación de campos obligatorios."""
        self._username = self._validate_username(username)
        self._password = self._validate_password(password)

    @staticmethod
    def _validate_username(username):
        """Valida que el nombre de usuario no esté vacío."""
        if username is None or str(username).strip() == "":
            raise ValueError("El nombre de usuario no puede estar vacío.")
        return str(username).strip()

    @staticmethod
    def _validate_password(password):
        """Valida que la contraseña no esté vacía."""
        if password is None or str(password).strip() == "":
            raise ValueError("La contraseña no puede estar vacía.")
        return str(password).strip()

    def set_username(self, username):
        """Establece un nombre de usuario validado."""
        self._username = self._validate_username(username)

    def set_password(self, password):
        """Establece una contraseña validada."""
        self._password = self._validate_password(password)

    def get_username(self):
        """Obtiene el nombre de usuario almacenado."""
        return self._username

    def get_password(self):
        """Obtiene la contraseña almacenada."""
        return self._password

    def validate_credentials(self, username, password):
        """Valida las credenciales ingresadas contra las del sistema."""
        username_clean = self._validate_username(username)
        password_clean = self._validate_password(password)
        return username_clean == self._username and password_clean == self._password


class AutoLavado:
    """Representa un vehículo que entra y sale del lavadero."""

    def __init__(self, plate, entry_time, hourly_rate):
        """Inicializa el vehículo con validación de datos."""
        self._plate = self._validate_plate(plate)
        self._entry_time = self._validate_time(entry_time)
        self._hourly_rate = self._validate_hourly_rate(hourly_rate)
        self._exit_time = None

    @staticmethod
    def _validate_plate(plate):
        """Valida que la placa no esté vacía y tenga una longitud mínima."""
        if plate is None or str(plate).strip() == "":
            raise ValueError("La placa no puede estar vacía.")
        plate_clean = str(plate).strip().upper()
        if len(plate_clean) < 6:
            raise ValueError("La placa debe tener al menos 6 caracteres.")
        return plate_clean

    @staticmethod
    def _validate_time(time_value):
        """Valida y normaliza una hora de ingreso o salida con formato HH:MM."""
        if isinstance(time_value, datetime):
            return time_value.replace(second=0, microsecond=0)

        if time_value is None or str(time_value).strip() == "":
            raise ValueError("La hora no puede estar vacía.")

        try:
            return datetime.strptime(str(time_value).strip(), "%H:%M").replace(second=0, microsecond=0)
        except ValueError:
            raise ValueError("La hora debe estar en formato HH:MM.")

    @staticmethod
    def _validate_hourly_rate(hourly_rate):
        """Valida que la tarifa por hora sea mayor que cero."""
        try:
            rate = float(hourly_rate)
        except (TypeError, ValueError):
            raise ValueError("La tarifa por hora debe ser numérica.")
        if rate <= 0:
            raise ValueError("La tarifa por hora debe ser mayor que cero.")
        return rate

    def set_plate(self, plate):
        """Establece una placa validada."""
        self._plate = self._validate_plate(plate)

    def set_entry_time(self, entry_time):
        """Establece la hora de ingreso validada."""
        self._entry_time = self._validate_time(entry_time)

    def set_exit_time(self, exit_time):
        """Establece la hora de salida validada."""
        exit_clean = self._validate_time(exit_time)
        if exit_clean < self._entry_time:
            raise ValueError("La hora de salida no puede ser menor que la de ingreso.")
        self._exit_time = exit_clean

    def set_hourly_rate(self, hourly_rate):
        """Establece la tarifa por hora validada."""
        self._hourly_rate = self._validate_hourly_rate(hourly_rate)

    def get_plate(self):
        """Obtiene la placa del vehículo."""
        return self._plate

    def get_entry_time(self):
        """Obtiene la hora de ingreso en formato HH:MM."""
        if self._entry_time is None:
            return ""
        return self._entry_time.strftime("%H:%M")

    def get_exit_time(self):
        """Obtiene la hora de salida en formato HH:MM."""
        if self._exit_time is None:
            return ""
        return self._exit_time.strftime("%H:%M")

    def get_hourly_rate(self):
        """Obtiene la tarifa por hora."""
        return self._hourly_rate

    def register_entry(self, entry_time):
        """Registra la hora de ingreso del vehículo."""
        self.set_entry_time(entry_time)

    def register_exit(self, exit_time):
        """Registra la hora de salida del vehículo validando el rango."""
        self.set_exit_time(exit_time)

    def calculate_payment(self, exit_time=None):
        """Calcula el total a pagar por el servicio de lavado."""
        if exit_time is not None:
            self.register_exit(exit_time)
        if self._exit_time is None:
            raise ValueError("Debe registrar primero la hora de salida.")

        duration_seconds = (self._exit_time - self._entry_time).total_seconds()
        billed_hours = max(1, math.ceil(duration_seconds / 3600))
        return billed_hours * self._hourly_rate

    def get_total_duration(self):
        """Obtiene el tiempo total transcurrido en horas y minutos."""
        if self._exit_time is None:
            raise ValueError("Debe registrar primero la hora de salida.")

        total_minutes = int((self._exit_time - self._entry_time).total_seconds() // 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return hours, minutes


class App(tk.Tk):
    """Interfaz principal para el sistema de autolavado."""

    def __init__(self):
        """Inicializa la ventana principal y la sesión del sistema."""
        super().__init__()
        self.title("Phase 2 Exercise 3 - Carwash")
        self.geometry("660x480")

        self.user_db = User()
        self.current_frame = None
        self.cars_in_service = []
        self.hourly_rate = 3000
        self.clock_var = tk.StringVar()

        # Se inicia directamente en la pantalla de login.
        self.show_login()

    def clear_screen(self):
        """Limpia el contenido activo de la ventana."""
        if self.current_frame is not None:
            self.current_frame.destroy()

    def show_login(self):
        """Muestra la pantalla de inicio de sesión."""
        self.clear_screen()

        # Contenedor para los elementos del login.
        self.current_frame = tk.Frame(self)
        self.current_frame.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(self.current_frame, text="User:").pack(anchor="w", pady=(10, 2))
        self.entry_user = tk.Entry(self.current_frame)
        self.entry_user.pack(fill="x", pady=(0, 10))

        tk.Label(self.current_frame, text="Password:").pack(anchor="w", pady=(0, 2))
        self.entry_password = tk.Entry(self.current_frame, show="*")
        self.entry_password.pack(fill="x", pady=(0, 15))

        btn_login = tk.Button(
            self.current_frame,
            text="Sign in",
            command=self.process_login,
        )
        btn_login.pack(fill="x")

    def process_login(self):
        """Procesa el inicio de sesión con validación de campos vacíos."""
        user_value = self.entry_user.get()
        password_value = self.entry_password.get()

        try:
            valid_user = User._validate_username(user_value)
            valid_password = User._validate_password(password_value)
            if self.user_db.validate_credentials(valid_user, valid_password):
                messagebox.showinfo("Great", "Login success!")
                self.show_core_feature()
            else:
                messagebox.showerror("Error", "User or password incorrect.")
        except ValueError as error:
            messagebox.showwarning("Alert!", str(error))

    def show_core_feature(self):
        """Muestra la pantalla principal del sistema de lavado."""
        self.clear_screen()

        # Esta es la vista después del login.
        self.current_frame = tk.Frame(self)
        self.current_frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.clock_label = tk.Label(
            self.current_frame,
            textvariable=self.clock_var,
            font=(SYSTEM_FONT, 10, "bold"),
            fg="darkblue",
        )
        self.clock_label.pack(anchor="e", pady=(0, 10))
        self.update_clock()

        tk.Label(
            self.current_frame,
            text="Car Wash",
            font=(SYSTEM_FONT, 12, "bold"),
        ).pack(pady=(0, 10))

        frame_entry = tk.Frame(self.current_frame)
        frame_entry.pack(fill="x", pady=10)

        tk.Label(frame_entry, text="License plate:").grid(row=0, column=0, padx=5)
        self.entry_plate = tk.Entry(frame_entry)
        self.entry_plate.grid(row=0, column=1, padx=5, sticky="ew")

        self.entry_time = tk.Entry(frame_entry, width=15, state="readonly")
        self.entry_time.grid(row=0, column=2, padx=5)
        self.entry_time.insert(0, datetime.now().strftime("%H:%M"))

        btn_register = tk.Button(frame_entry, text="Check in", command=self.register_car)
        btn_register.grid(row=0, column=3, padx=10)

        frame_entry.grid_columnconfigure(1, weight=1)

        columns = ("plate", "entry_time", "hourly_rate")
        self.car_list = ttk.Treeview(self.current_frame, columns=columns, show="headings", height=10)
        self.car_list.heading("plate", text="License Plate")
        self.car_list.heading("entry_time", text="Checkin time")
        self.car_list.heading("hourly_rate", text="Hourly rate")
        self.car_list.column("plate", anchor="center", width=180)
        self.car_list.column("entry_time", anchor="center", width=150)
        self.car_list.column("hourly_rate", anchor="center", width=130)
        self.car_list.pack(fill="both", expand=True, pady=10)

        frame_exit = tk.Frame(self.current_frame)
        frame_exit.pack(fill="x", pady=10)

        self.entry_exit_time = tk.Entry(frame_exit, width=15, state="readonly")
        self.entry_exit_time.grid(row=0, column=0, padx=5)
        self.entry_exit_time.insert(0, datetime.now().strftime("%H:%M"))

        btn_exit = tk.Button(frame_exit, text="Check out", command=self.register_exit_car)
        btn_exit.grid(row=0, column=1, padx=10)

    def update_clock(self):
        """Actualiza la hora del sistema en la ventana principal."""
        self.clock_var.set(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        self.after(1000, self.update_clock)

    def register_car(self):
        """Registra un vehículo con validaciones de placa y hora de ingreso."""
        plate_value = self.entry_plate.get()
        entry_time_value = datetime.now()

        try:
            plate_clean = AutoLavado._validate_plate(plate_value)
            entry_time_clean = AutoLavado._validate_time(entry_time_value)
            auto = AutoLavado(plate_clean, entry_time_clean, self.hourly_rate)
            self.cars_in_service.append(auto)
            self.entry_time.config(state="normal")
            self.entry_time.delete(0, tk.END)
            self.entry_time.insert(0, entry_time_clean.strftime("%H:%M"))
            self.entry_time.config(state="readonly")
            self.update_car_list()
            messagebox.showinfo("Success!", f"Car {plate_clean} registered.")
            self.entry_plate.delete(0, tk.END)
            self.entry_plate.focus_set()
        except ValueError as error:
            messagebox.showwarning("Alert!", str(error))
            self.entry_plate.focus_set()

    def update_car_list(self):
        """Actualiza la lista de vehículos activos con columnas y encabezados."""
        for row in self.car_list.get_children():
            self.car_list.delete(row)

        for auto in self.cars_in_service:
            self.car_list.insert(
                "",
                tk.END,
                values=(auto.get_plate(), auto.get_entry_time(), f"{auto.get_hourly_rate():,.0f}"),
            )

    def register_exit_car(self):
        """Registra la salida de un vehículo y calcula el total a pagar."""
        selection = self.car_list.selection()
        if not selection:
            messagebox.showwarning("Alert!", "Please select a car from the list.")
            return

        exit_time_value = datetime.now()
        try:
            exit_time_clean = AutoLavado._validate_time(exit_time_value)
            self.entry_exit_time.config(state="normal")
            self.entry_exit_time.delete(0, tk.END)
            self.entry_exit_time.insert(0, exit_time_clean.strftime("%H:%M"))
            self.entry_exit_time.config(state="readonly")

            index = self.car_list.index(selection[0])
            auto = self.cars_in_service[index]
            total = auto.calculate_payment(exit_time_clean)
            hours, minutes = auto.get_total_duration()

            receipt = (
                f"Plate: {auto.get_plate()}\n"
                f"Check-in time: {auto.get_entry_time()}\n"
                f"Check-out time: {exit_time_clean.strftime('%H:%M')}\n"
                f"Total time: {hours} hours y {minutes} minutes\n"
                f"Total due: ${total:,.0f}"
            )

            self.cars_in_service.pop(index)
            self.update_car_list()
            messagebox.showinfo("Cobro", receipt)
            self.entry_plate.focus_set()
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            self.entry_plate.focus_set()


if __name__ == "__main__":
    app = App()
    app.mainloop()