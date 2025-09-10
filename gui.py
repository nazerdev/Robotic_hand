import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports

# Colores para modo oscuro
BG_COLOR = "#000000"
FG_COLOR = "#f0f0f0"
ACCENT_COLOR = "#4caf50"
BUTTON_BG = "#3a3a3a"
BUTTON_HOVER = "#5cb85c"
TEXT_BG = "#1e1e1e"
TEXT_FG = "#dcdcdc"
ERROR_COLOR = "#e74c3c"

def listar_puertos():
    puertos = serial.tools.list_ports.comports()
    lista = [p.device for p in puertos]
    menu_puertos['values'] = lista
    if lista:
        puerto_var.set(lista[0])
    else:
        puerto_var.set('')

def conectar():
    global ser
    try:
        ser = serial.Serial(puerto_var.get(), int(baud_var.get()), timeout=0)
        estado.set("Conectado")
        btn_conectar.config(state='disabled')
        btn_desconectar.config(state='normal')
        mostrar_datos()
    except Exception as e:
        estado.set(f"Error: {e}")
        label_estado.config(foreground=ERROR_COLOR)

def desconectar():
    global ser
    if ser and ser.is_open:
        ser.close()
    estado.set("Desconectado")
    label_estado.config(foreground=FG_COLOR)
    btn_conectar.config(state='normal')
    btn_desconectar.config(state='disabled')

def mostrar_datos():
    if ser and ser.is_open:
        data = ser.read(ser.in_waiting or 1)
        if data:
            texto.config(state='normal')
            texto.insert("end", data.decode(errors="ignore"))
            texto.see("end")
            texto.config(state='disabled')
        root.after(100, mostrar_datos)

def on_enter(e):
    e.widget['background'] = BUTTON_HOVER

def on_leave(e):
    e.widget['background'] = BUTTON_BG

root = tk.Tk()
root.title("Robotic Hand Serial")
root.geometry("650x450")
root.configure(bg=BG_COLOR)
root.resizable(False, False)
root.eval('tk::PlaceWindow . center')

# Variables
puerto_var = tk.StringVar()
baud_var = tk.StringVar(value="115200")
estado = tk.StringVar(value="Desconectado")
ser = None

# Fuente moderna
font_label = ("Segoe UI", 11)
font_entry = ("Segoe UI", 11)
font_button = ("Segoe UI Semibold", 11)
font_text = ("Consolas", 11)

# Frame configuración
frame_config = tk.Frame(root, bg=BG_COLOR)
frame_config.place(x=20, y=20, width=610, height=110)

# Puerto
label_puerto = tk.Label(frame_config, text="Puerto:", bg=BG_COLOR, fg=FG_COLOR, font=font_label)
label_puerto.place(x=10, y=10)

menu_puertos = ttk.Combobox(frame_config, textvariable=puerto_var, state="readonly", width=20, font=font_entry)
menu_puertos.place(x=80, y=10)

btn_actualizar = tk.Label(frame_config, text="⟳", bg=BUTTON_BG, fg=FG_COLOR, font=("Segoe UI", 14), width=3, cursor="hand2")
btn_actualizar.place(x=260, y=7)
btn_actualizar.bind("<Button-1>", lambda e: listar_puertos())
btn_actualizar.bind("<Enter>", on_enter)
btn_actualizar.bind("<Leave>", on_leave)

# Baudrate
label_baud = tk.Label(frame_config, text="Baudrate:", bg=BG_COLOR, fg=FG_COLOR, font=font_label)
label_baud.place(x=10, y=50)

entry_baud = tk.Entry(frame_config, textvariable=baud_var, font=font_entry, width=23, bg=TEXT_BG, fg=TEXT_FG, insertbackground=FG_COLOR, relief='flat')
entry_baud.place(x=80, y=50)

# Botones conectar/desconectar
btn_conectar = tk.Label(frame_config, text="Conectar", bg=BUTTON_BG, fg=FG_COLOR, font=font_button, width=15, cursor="hand2", relief='flat')
btn_conectar.place(x=350, y=10)
btn_conectar.bind("<Button-1>", lambda e: conectar())
btn_conectar.bind("<Enter>", on_enter)
btn_conectar.bind("<Leave>", on_leave)

btn_desconectar = tk.Label(frame_config, text="Desconectar", bg=BUTTON_BG, fg=FG_COLOR, font=font_button, width=15, cursor="hand2", relief='flat', state='disabled')
btn_desconectar.place(x=350, y=50)
btn_desconectar.bind("<Button-1>", lambda e: desconectar())
btn_desconectar.bind("<Enter>", on_enter)
btn_desconectar.bind("<Leave>", on_leave)
btn_desconectar.config(state='disabled')

def set_btn_state(btn, state):
    if state == 'normal':
        btn.config(state='normal', fg=FG_COLOR)
    else:
        btn.config(state='disabled', fg="#555555")

def conectar():
    global ser
    try:
        ser = serial.Serial(puerto_var.get(), int(baud_var.get()), timeout=0)
        estado.set("Conectado")
        label_estado.config(fg=ACCENT_COLOR)
        set_btn_state(btn_conectar, 'disabled')
        set_btn_state(btn_desconectar, 'normal')
        mostrar_datos()
    except Exception as e:
        estado.set(f"Error: {e}")
        label_estado.config(fg=ERROR_COLOR)

def desconectar():
    global ser
    if ser and ser.is_open:
        ser.close()
    estado.set("Desconectado")
    label_estado.config(fg=FG_COLOR)
    set_btn_state(btn_conectar, 'normal')
    set_btn_state(btn_desconectar, 'disabled')

# Frame datos
frame_datos = tk.Frame(root, bg=BG_COLOR)
frame_datos.place(x=20, y=150, width=610, height=280)

scrollbar = tk.Scrollbar(frame_datos)
scrollbar.pack(side='right', fill='y')

texto = tk.Text(frame_datos, height=15, width=70, state='disabled', yscrollcommand=scrollbar.set,
                bg=TEXT_BG, fg=TEXT_FG, insertbackground=FG_COLOR, font=font_text, relief='flat')
texto.pack(side='left', fill='both', expand=True)
scrollbar.config(command=texto.yview)

# Estado
label_estado = tk.Label(root, textvariable=estado, bg=BG_COLOR, fg=FG_COLOR, font=("Segoe UI", 12, "bold"))
label_estado.place(x=20, y=440)

# Inicializar puertos
listar_puertos()

root.mainloop()
