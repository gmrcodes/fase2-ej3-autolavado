import tkinter as tk
from tkinter import messagebox


class Usuario:

  def __init__(self, user="123", password="123"):
    self._usuario = user
    self._password = password

  def validar(self, usuario_ingresado, password_ingresada):
    return usuario_ingresado == self._usuario and password_ingresada == self._password

class AutoLavado:
  def __init__(self, placa, hora_ingreso, tarifa_hora):
    self._placa = placa
    self._hora_ingreso = hora_ingreso
    self._tarifa_hora = tarifa_hora
    self._hora_salida = None

  def registrar_ingreso(self, hora):
    self._hora_ingreso = hora

  def  registrar_salida(self, hora):
    if hora < self._hora_ingreso:
      return False
    self._hora_salida = hora
    return True

  def calcular_pago(self, hora_salida):
    horas = hora_salida - self._hora_ingreso
    if horas < 1:
      horas = 1

    return horas * self._tarifa_hora

  def get_placa(self):
    return self._placa

  def get_hora_ingreso(self):
    return self._hora_ingreso

class App(tk.Tk):

  def __init__(self):
    super().__init__()
    self.title("Phase 2 Exercise 3 - Carwash")
    self.geometry("660x480")

    self.usuario_db = Usuario()
    self.frame_actual = None

    self.fila_carros = []
    self.tarifa_hora = 5000

    # Iniciar directamente en la pantalla de login
    self.show_login()

  def clear_screen(self):
    if self.frame_actual is not None:
      self.frame_actual.destroy()

  def show_login(self):
    self.clear_screen()

    # Contenedor para los elementos del login
    self.frame_actual = tk.Frame(self)
    self.frame_actual.pack(expand=True, fill="both", padx=20, pady=20)

    # Componentes de la interfaz
    tk.Label(self.frame_actual, text="User:").pack(anchor="w", pady=(10, 2))
    entry_user = tk.Entry(self.frame_actual)
    entry_user.pack(fill="x", pady=(0, 10))

    tk.Label(self.frame_actual, text="Password:").pack(anchor="w", pady=(0, 2))
    entry_pass = tk.Entry(self.frame_actual, show="*")
    entry_pass.pack(fill="x", pady=(0, 15))

    btn_login = tk.Button(
        self.frame_actual,
        text="Sign in",
        command=lambda: self.process_login(entry_user.get(), entry_pass.get()),
    )
    btn_login.pack(fill="x")

  def process_login(self, user, password):
    if self.usuario_db.validar(user, password):
      messagebox.showinfo("Great", "Login success!.")
      self.show_core_feature()
    else:
      messagebox.showerror("Error", "User or password incorrect.")

  def show_core_feature(self):
    self.clear_screen()

    # Esta es la vista después del login
    self.frame_actual = tk.Frame(self)
    self.frame_actual.pack(expand=True, fill="both", padx=20, pady=20)

    # Titulo
    tk.Label(
        self.frame_actual,
        text="Car Wash",
        font=("Arial", 11, "bold"),
    ).pack(pady=10)

    # Vista de registrar ingreso
    frame_ingreso = tk.Frame(self.frame_actual)
    frame_ingreso.pack(pady=10)

    tk.Label(frame_ingreso, text="License plate:").grid(row=0,column=0,padx=5)
    self.entry_placa = tk.Entry(frame_ingreso)
    self.entry_placa.grid(row=0,column=1,padx=5)

    tk.Label(frame_ingreso, text="Start time (0-23):").grid(row=0,column=2,padx=5)
    self.entry_hora = tk.Entry(frame_ingreso, width=10)
    self.entry_hora.grid(row=0,column=3,padx=5)

    btn_registro = tk.Button(frame_ingreso, text="Check in", command=self.registrar_auto)
    btn_registro.grid(row=0,column=4,padx=10)

    # Vista de Lista de autos
    self.lista_autos = tk.Listbox(self.frame_actual, width=60, height=10)
    self.lista_autos.pack(pady=10)

    # Vista de frame para salida
    frame_salida = tk.Frame(self.frame_actual)
    frame_salida.pack(pady=10)
    
    tk.Label(frame_salida, text="Time out (0-23):").grid(row=0, column=0, padx=5)
    self.entry_hora_salida = tk.Entry(frame_salida, width=10)
    self.entry_hora_salida.grid(row=0, column=1, padx=5)
    
    btn_salida = tk.Button(frame_salida, text="Check out",
              command=self.registrar_salida_auto).grid(row=0, column=2, padx=10)
    
    # Label para mostrar total
    self.label_total = tk.Label(self.frame_actual, text="", 
                                 font=("Arial", 12, "bold"), fg="green")
    self.label_total.pack(pady=5)

  def registrar_auto(self):
    self.label_total.config(text="")
    placa = self.entry_placa.get().upper().strip()
    # Validar ingreso de placa
    if not placa or len(placa) < 6:
      messagebox.showwarning("Alert!", "Enter a valid license plate.")
      self.entry_placa.focus_set()
      return

    try:
      hora = int(self.entry_hora.get())
      if 0 <= hora <= 23:
          auto = AutoLavado(placa, hora, self.tarifa_hora)
          self.fila_carros.append(auto)
          self.actualizar_lista()
          messagebox.showinfo("Success!", f"Car {placa} registered")
          self.entry_hora.delete(0,tk.END)
          self.entry_placa.delete(0,tk.END)
          self.entry_placa.focus_set()
      else:
          messagebox.showerror("Error", "Invalid time (0-23)")
    except ValueError:
        messagebox.showerror("Error", "Start time must be a number")
        self.entry_hora.focus_set()

  def actualizar_lista(self):
      self.lista_autos.delete(0, tk.END)
      for i, auto in enumerate(self.fila_carros):
          self.lista_autos.insert(tk.END, 
              f"{i+1}. License plate: {auto.get_placa()} - Checkin: {auto.get_hora_ingreso()}:00")

  def registrar_salida_auto(self):
      seleccion = self.lista_autos.curselection()
      if not seleccion:
          messagebox.showwarning("Alert!", "Please select a car from list")
          return
      
      try:
          hora_salida = int(self.entry_hora_salida.get())
          idx = seleccion[0]
          auto = self.fila_carros[idx]
          
          if auto.registrar_salida(hora_salida):
              total = auto.calcular_pago(hora_salida)
              self.label_total.config(text=f"Total: ${total:,.0f}")
              self.fila_carros.pop(idx)
              self.actualizar_lista()
              messagebox.showinfo("Paid", f"Total: ${total:,.0f}")
              self.entry_hora_salida.delete(0,tk.END)
              self.entry_placa.focus_set()
          else:
              messagebox.showerror("Error", "Failed to register")              
      except ValueError:
          messagebox.showerror("Error", "Time out must be a number")
          self.entry_hora_salida.focus_set()


if __name__ == "__main__":
  app = App()
  app.mainloop()