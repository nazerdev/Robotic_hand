import os
import tkinter as tk
from tkinter import messagebox
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from PIL import Image, ImageTk

# --- Utilidad para rutas de archivos (imagenes, etc.) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def asset_path(nombre: str) -> str:
    """Devuelve la ruta absoluta de un recurso ubicado junto al script."""
    return os.path.join(BASE_DIR, nombre)

# Clase Usuario
class Usuario:
    def __init__(self, usuario, email, password_hash, rol):
        self.usuario = usuario
        self.email = email
        self.password_hash = password_hash
        self.rol = rol

    def guardar_en_db(self):
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                rol TEXT NOT NULL
            )
        ''')
        try:
            cursor.execute('''
                INSERT INTO usuarios (usuario, email, password_hash, rol)
                VALUES (?, ?, ?, ?)
            ''', (self.usuario, self.email, self.password_hash, self.rol))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return False  # Usuario ya existe
        conn.close()
        return True

    @staticmethod
    def obtener_por_usuario(usuario):
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        cursor.execute('SELECT usuario, email, password_hash, rol FROM usuarios WHERE usuario = ?', (usuario,))
        fila = cursor.fetchone()
        conn.close()
        if fila:
            return Usuario(*fila)
        else:
            return None

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Login Mano Robótica")
        self.root.configure(bg="#2c3e50")
        self.centrar_ventana(600, 450)
        self.usuario_logueado = None
        self.ventana_login()

    def centrar_ventana(self, ancho=400, alto=400):
        self.root.geometry(f"{ancho}x{alto}")
        self.root.update_idletasks()
        ancho_ventana = self.root.winfo_width()
        alto_ventana = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (ancho_ventana // 2)
        y = (self.root.winfo_screenheight() // 2) - (alto_ventana // 2)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

    def limpiar_ventana(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def crear_label(self, texto, tamaño=16, negrita=False):
        fuente = ("Arial", tamaño, "bold" if negrita else "normal")
        return tk.Label(self.root, text=texto, font=fuente, bg="#2c3e50", fg="#ecf0f1")

    def crear_entry(self):
        entry = tk.Entry(self.root, font=("Arial", 14), bg="#34495e", fg="#ecf0f1",
                         insertbackground="#ecf0f1", relief="flat")
        return entry

    def crear_boton(self, texto, comando):
        boton = tk.Button(self.root, text=texto, font=("Arial", 14), bg="#1abc9c", fg="white",
                          activebackground="#16a085", activeforeground="white",
                          relief="flat", command=comando, cursor="hand2")
        boton.bind("<Enter>", lambda e: boton.config(bg="#16a085"))
        boton.bind("<Leave>", lambda e: boton.config(bg="#1abc9c"))
        return boton

    def ventana_login(self):
        self.limpiar_ventana()

        frame_principal = tk.Frame(self.root, bg="#2c3e50")
        frame_principal.pack(expand=True, fill="both")

        # Frame para imagen (izquierda)
        frame_imagen = tk.Frame(frame_principal, bg="#2c3e50", width=200, height=400)
        frame_imagen.pack(side="left", fill="y", padx=10, pady=10)

        # --- Carga segura de la imagen desde la misma carpeta del script ---
        ruta_img = asset_path("BR2.png")  # cambia el nombre si usás otro
        try:
            img = Image.open(ruta_img)
            # Compatibilidad con Pillow nuevo y viejo:
            try:
                img = img.resize((200, 400), Image.Resampling.LANCZOS)
            except Exception:
                img = img.resize((200, 400), Image.ANTIALIAS)

            self.imagen_tk = ImageTk.PhotoImage(img)   # mantener referencia
            label_imagen = tk.Label(frame_imagen, image=self.imagen_tk, bg="#0b4176")
            label_imagen.pack(expand=True)
        except Exception as e:
            tk.Label(frame_imagen, text=f"Imagen no encontrada\n{os.path.basename(ruta_img)}",
                     fg="red", bg="#2c3e50").pack(expand=True)
            # Para depuración opcional:
            print(f"[ERROR] No se pudo cargar la imagen: {ruta_img}\n{e}")

        # Frame para formulario (derecha)
        frame_form = tk.Frame(frame_principal, bg="#2c3e50")
        frame_form.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        label_titulo = self.crear_label("Login", 24, True)
        label_titulo.pack(pady=(0, 15), in_=frame_form)

        label_usuario = self.crear_label("Usuario:", 16)
        label_usuario.pack(anchor="w", padx=10, in_=frame_form)
        self.entry_usuario = self.crear_entry()
        self.entry_usuario.pack(pady=5, padx=10, fill="x", in_=frame_form)

        label_password = self.crear_label("Contraseña:", 16)
        label_password.pack(anchor="w", padx=10, in_=frame_form)
        self.entry_password = self.crear_entry()
        self.entry_password.config(show="*")
        self.entry_password.pack(pady=5, padx=10, fill="x", in_=frame_form)

        boton_entrar = self.crear_boton("Entrar", self.login)
        boton_entrar.pack(pady=20, padx=10, fill="x", in_=frame_form)

        boton_registro = tk.Button(frame_form, text="Registrarse", font=("Arial", 12),
                                   bg="#34495e", fg="#1abc9c", relief="flat",
                                   command=self.ventana_registro, cursor="hand2")
        boton_registro.pack()
        boton_registro.bind("<Enter>", lambda e: boton_registro.config(fg="#16a085"))
        boton_registro.bind("<Leave>", lambda e: boton_registro.config(fg="#1abc9c"))

    def ventana_registro(self):
        self.limpiar_ventana()

        self.crear_label("Registro", 24, True).pack(pady=(20, 15))

        self.crear_label("Usuario:", 16).pack(anchor="w", padx=50)
        self.entry_usuario_reg = self.crear_entry()
        self.entry_usuario_reg.pack(pady=5, padx=50, fill="x")

        self.crear_label("Email:", 16).pack(anchor="w", padx=50)
        self.entry_email_reg = self.crear_entry()
        self.entry_email_reg.pack(pady=5, padx=50, fill="x")

        self.crear_label("Contraseña:", 16).pack(anchor="w", padx=50)
        self.entry_password_reg = self.crear_entry()
        self.entry_password_reg.config(show="*")
        self.entry_password_reg.pack(pady=5, padx=50, fill="x")

        self.crear_label("Rol:", 16).pack(anchor="w", padx=50, pady=(10,0))
        self.rol_var = tk.StringVar(value="usuario")
        frame_rol = tk.Frame(self.root, bg="#2c3e50")
        frame_rol.pack(pady=5)
        tk.Radiobutton(frame_rol, text="Admin", variable=self.rol_var, value="admin",
                       font=("Arial", 14), bg="#2c3e50", fg="#ecf0f1",
                       selectcolor="#1abc9c", activebackground="#2c3e50",
                       activeforeground="#ecf0f1").pack(side="left", padx=20)
        tk.Radiobutton(frame_rol, text="Usuario", variable=self.rol_var, value="usuario",
                       font=("Arial", 14), bg="#2c3e50", fg="#ecf0f1",
                       selectcolor="#1abc9c", activebackground="#2c3e50",
                       activeforeground="#ecf0f1").pack(side="left", padx=20)

        self.crear_boton("Registrar", self.registrar).pack(pady=20, padx=50, fill="x")
        boton_volver = tk.Button(self.root, text="Volver al Login", font=("Arial", 12),
                                 bg="#34495e", fg="#1abc9c", relief="flat",
                                 command=self.ventana_login, cursor="hand2")
        boton_volver.pack()
        boton_volver.bind("<Enter>", lambda e: boton_volver.config(fg="#16a085"))
        boton_volver.bind("<Leave>", lambda e: boton_volver.config(fg="#1abc9c"))

    def login(self):
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get()

        user = Usuario.obtener_por_usuario(usuario)
        if user:
            if check_password_hash(user.password_hash, password):
                self.usuario_logueado = user.usuario
                self.ventana_principal()
            else:
                messagebox.showerror("Error", "Contraseña incorrecta")
        else:
            messagebox.showerror("Error", "Usuario no encontrado")

    def registrar(self):
        usuario = self.entry_usuario_reg.get().strip()
        email = self.entry_email_reg.get().strip()
        password = self.entry_password_reg.get()
        rol = self.rol_var.get()

        if not usuario or not email or not password:
            messagebox.showwarning("Atención", "Completa todos los campos")
            return

        password_hash = generate_password_hash(password)
        nuevo_usuario = Usuario(usuario, email, password_hash, rol)
        if not nuevo_usuario.guardar_en_db():
            messagebox.showerror("Error", "El nombre de usuario ya existe")
            return

        messagebox.showinfo("Éxito", "Usuario registrado correctamente")
        self.ventana_login()

    def ventana_principal(self):
        self.limpiar_ventana()
        usuario = self.usuario_logueado
        user = Usuario.obtener_por_usuario(usuario)
        rol = user.rol if user else "Desconocido"

        self.crear_label(f"Bienvenido {usuario}", 24, True).pack(pady=30)
        self.crear_label(f"Rol: {rol}", 18).pack(pady=10)
        self.crear_boton("Cerrar sesión", self.cerrar_sesion).pack(pady=30, padx=100, fill="x")

    def cerrar_sesion(self):
        self.usuario_logueado = None
        self.ventana_login()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
