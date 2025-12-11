import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import csv
import copy 
import numpy as np 

# ------------------------------------------------------------------
# MODELO (Lógica de Negocio)
# ------------------------------------------------------------------

class Jugador:
    def __init__(self, nombre, posicion, resistencia):
        self.nombre = nombre
        self.posicion = posicion
        # La resistencia se convierte a float para usarla con NumPy en la simulación
        self.resistencia = float(resistencia) 
        self.resistencia_max = float(resistencia)
        
        # Definir perfil ofensivo/defensivo según posición
        pos = posicion.lower()
        if pos in ["portero", "defensa"]:
            self.defensa = 0.8
            self.ataque = 0.2
        elif pos == "mediocampista":
            self.defensa = 0.5
            self.ataque = 0.5
        elif pos == "delantero":
            self.defensa = 0.2
            self.ataque = 0.8
        else:
            self.defensa = 0.5
            self.ataque = 0.5

    def cansar(self, cantidad):
        """Reduce la resistencia. La cantidad ya puede ser un float de NumPy."""
        self.resistencia -= cantidad
        if self.resistencia < 0: self.resistencia = 0

class Equipo:
    def __init__(self, nombre_equipo, lista_jugadores):
        self.nombre = nombre_equipo
        self.goles = 0
        
        if len(lista_jugadores) >= 11:
            self.titulares = lista_jugadores[:11]
            self.banca = lista_jugadores[11:]
        else:
            self.titulares = lista_jugadores
            self.banca = []
            
        self.cambios_realizados = 0
        self.tactica_actual = "Neutro" 

    def calcular_tactica(self):
        """
        Calcula la táctica usando np.sum() para una suma vectorial más eficiente.
        """
        # Extraer atributos a un array de NumPy
        ataques = np.array([j.ataque for j in self.titulares])
        defensas = np.array([j.defensa for j in self.titulares])
        
        # Suma vectorial (mucho más rápida)
        total_ataque = np.sum(ataques)
        total_defensa = np.sum(defensas)
        
        if total_ataque > total_defensa + 1: 
            self.tactica_actual = "OFENSIVA"
        elif total_defensa > total_ataque + 1:
            self.tactica_actual = "DEFENSIVA"
        else:
            self.tactica_actual = "EQUILIBRADA"
            
        return total_ataque, total_defensa

    def verificar_cambios(self, minuto):
        """
        Verifica cambios por baja resistencia (Lógica sin NumPy, basada en objetos).
        """
        mensajes = []
        if self.cambios_realizados >= 5:
            return mensajes

        indices_a_cambiar = []
        for i, jugador in enumerate(self.titulares):
            if jugador.resistencia < (jugador.resistencia_max * 0.3) and self.banca:
                indices_a_cambiar.append(i)
        
        for i in indices_a_cambiar:
            if self.cambios_realizados >= 5:
                break
                
            jugador = self.titulares[i]
            
            reemplazo = None
            for suplente in self.banca:
                if suplente.posicion == jugador.posicion:
                    reemplazo = suplente
                    break
            
            if not reemplazo and self.banca:
                reemplazo = self.banca[0]
            
            if reemplazo:
                self.titulares[i] = reemplazo
                self.banca.remove(reemplazo)
                self.cambios_realizados += 1
                
                mensajes.append(f"🔄 CAMBIO en {self.nombre} al min {minuto}: "
                                f"Sale {jugador.nombre} ({jugador.posicion}) cansado, "
                                f"Entra {reemplazo.nombre} ({reemplazo.posicion}).")
                
        return mensajes

# ------------------------------------------------------------------
# MOTOR DE SIMULACIÓN (Uso intensivo de NumPy)
# ------------------------------------------------------------------

class SimuladorPartido:
    def __init__(self, equipo_a, equipo_b):
        self.eq_a = copy.deepcopy(equipo_a)
        self.eq_b = copy.deepcopy(equipo_b)
        self.log = [] 
        self.eventos_clave = [] 

    def simular(self):
        self.log.append(f"--- INICIO DEL PARTIDO: {self.eq_a.nombre} vs {self.eq_b.nombre} ---")
        
        for minuto in range(1, 91):
            
            # 1. Calcular tácticas actuales (usa np.sum internamente)
            atq_a, def_a = self.eq_a.calcular_tactica()
            atq_b, def_b = self.eq_b.calcular_tactica()
            
            # 2. Verificar cambios por cansancio
            msgs_a = self.eq_a.verificar_cambios(minuto)
            msgs_b = self.eq_b.verificar_cambios(minuto)
            for m in msgs_a + msgs_b:
                self.log.append(m)
                self.eventos_clave.append(m)

            # 3. Probabilidad de Gol
            prob_gol_a = (atq_a / (def_b + 0.1)) * 0.015 
            prob_gol_b = (atq_b / (def_a + 0.1)) * 0.015

            # Intento de gol A
            if np.random.rand() < prob_gol_a: # np.random.rand() es el equivalente a random.random()
                autor = np.random.choice(self.eq_a.titulares) # np.random.choice() es el equivalente a random.choice()
                self.eq_a.goles += 1
                msg = f"⚽ ¡GOOOL de {self.eq_a.nombre}! (Min {minuto}) - {autor.nombre} ({autor.posicion})"
                self.log.append(msg)
                self.eventos_clave.append(msg)

            # Intento de gol B
            elif np.random.rand() < prob_gol_b:
                autor = np.random.choice(self.eq_b.titulares)
                self.eq_b.goles += 1
                msg = f"⚽ ¡GOOOL de {self.eq_b.nombre}! (Min {minuto}) - {autor.nombre} ({autor.posicion})"
                self.log.append(msg)
                self.eventos_clave.append(msg)
            
            # 4. Desgaste de jugadores (IMPLEMENTACIÓN CON NUMPY)
            factor_cansancio_a = 1.2 if self.eq_a.tactica_actual == "OFENSIVA" else 0.8
            factor_cansancio_b = 1.2 if self.eq_b.tactica_actual == "OFENSIVA" else 0.8
            
            # Generar un array de desgaste aleatorio de una sola vez
            desgaste_a = np.random.uniform(0.5, 1.5, size=len(self.eq_a.titulares)) * factor_cansancio_a
            desgaste_b = np.random.uniform(0.5, 1.5, size=len(self.eq_b.titulares)) * factor_cansancio_b

            # Aplicar el desgaste a los objetos Jugador usando zip
            for j, d in zip(self.eq_a.titulares, desgaste_a): j.cansar(d)
            for j, d in zip(self.eq_b.titulares, desgaste_b): j.cansar(d)

            # Log discreto de táctica
            if minuto % 15 == 0:
                self.log.append(f"⏱ Min {minuto} | Tácticas -> {self.eq_a.nombre}: {self.eq_a.tactica_actual} vs {self.eq_b.nombre}: {self.eq_b.tactica_actual}")

        self.log.append("--- FIN DEL PARTIDO ---")
        return self.log, self.eventos_clave

# ------------------------------------------------------------------
# INTERFAZ GRÁFICA (GUI) MEJORADA (sin cambios)
# ------------------------------------------------------------------

class InterfazFutbol:
    def __init__(self, root):
        self.root = root
        self.root.title("⚽ Simulador Táctico de Fútbol ⚽")
        self.root.geometry("750x650")
        
        COLOR_FONDO = "#E8E8E8"
        COLOR_PRIMARIO = "#4CAF50"
        COLOR_SECUNDARIO = "#34495E"
        COLOR_CONTRASTE = "#FFC300"
        
        self.root.config(bg=COLOR_FONDO)

        self.ruta_a = tk.StringVar(value="[Cargar archivo CSV del Equipo A]")
        self.ruta_b = tk.StringVar(value="[Cargar archivo CSV del Equipo B]")
        self.equipo_A = None
        self.equipo_B = None

        tk.Label(root, text="SIMULADOR DE PARTIDO TÁCTICO", 
                 font=("Arial", 18, "bold"), 
                 bg=COLOR_SECUNDARIO, 
                 fg="white", 
                 pady=10).pack(fill="x", padx=10, pady=(10, 5))

        frame_carga = tk.LabelFrame(root, text="📁 CARGA DE EQUIPOS (CSV)", 
                                    font=("Arial", 10, "bold"),
                                    bg="white", 
                                    fg=COLOR_SECUNDARIO, 
                                    padx=15, pady=10)
        frame_carga.pack(fill="x", padx=15, pady=10)

        tk.Button(frame_carga, text="CARGAR EQUIPO A", 
                  command=lambda: self.cargar_csv("A"), 
                  bg=COLOR_PRIMARIO, fg="white", 
                  font=("Arial", 10, "bold"), 
                  relief=tk.RAISED, bd=3).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        tk.Label(frame_carga, textvariable=self.ruta_a, 
                 bg=COLOR_FONDO, fg=COLOR_SECUNDARIO, 
                 anchor="w", width=60, relief=tk.SUNKEN, padx=5).grid(row=0, column=1, padx=10, sticky="ew")

        tk.Button(frame_carga, text="CARGAR EQUIPO B", 
                  command=lambda: self.cargar_csv("B"), 
                  bg=COLOR_PRIMARIO, fg="white", 
                  font=("Arial", 10, "bold"), 
                  relief=tk.RAISED, bd=3).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        tk.Label(frame_carga, textvariable=self.ruta_b, 
                 bg=COLOR_FONDO, fg=COLOR_SECUNDARIO, 
                 anchor="w", width=60, relief=tk.SUNKEN, padx=5).grid(row=1, column=1, padx=10, sticky="ew")

        self.btn_simular = tk.Button(root, text="¡INICIAR PARTIDO! 🥅", 
                                     command=self.ejecutar_simulacion, 
                                     bg="#9E9E9E", fg="white", 
                                     font=("Arial", 14, "bold"), 
                                     relief=tk.RAISED, bd=5, 
                                     state=tk.DISABLED) 
        self.btn_simular.pack(pady=15, padx=15, fill="x")

        frame_res = tk.LabelFrame(root, text="📢 RESULTADOS Y MINUTO A MINUTO", 
                                  font=("Arial", 10, "bold"),
                                  bg="white", 
                                  fg=COLOR_SECUNDARIO, 
                                  padx=15, pady=10)
        frame_res.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.lbl_marcador = tk.Label(frame_res, text="0 - 0", 
                                     font=("Courier", 36, "bold"), 
                                     bg=COLOR_SECUNDARIO, 
                                     fg=COLOR_CONTRASTE, 
                                     relief=tk.GROOVE,
                                     padx=20, pady=10, 
                                     anchor="center")
        self.lbl_marcador.pack(fill="x", pady=(5, 10))

        tk.Label(frame_res, text="Detalles del Juego:", 
                 bg="white", fg=COLOR_SECUNDARIO, 
                 font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.txt_reporte = scrolledtext.ScrolledText(frame_res, height=12, 
                                                     font=("Consolas", 9), 
                                                     bg="#F5F5F5", fg="#2C3E50", 
                                                     relief=tk.SUNKEN)
        self.txt_reporte.pack(fill="both", expand=True, pady=(5, 0))
        self.txt_reporte.insert(tk.END, "Esperando la carga de dos equipos y simulación...")


    def cargar_csv(self, equipo_letra):
        """Abre un diálogo de archivo y carga los datos del CSV."""
        ruta_archivo = filedialog.askopenfilename(
            title=f"Seleccionar archivo CSV para Equipo {equipo_letra}",
            filetypes=[("Archivos CSV", "*.csv")]
        )
        
        if not ruta_archivo:
            return 
        
        try:
            lista_jugadores = []
            nombre_equipo = ""
            
            with open(ruta_archivo, mode='r', newline='', encoding='utf-8') as archivo:
                lector = csv.DictReader(archivo)
                
                nombre_equipo = ruta_archivo.split('/')[-1].replace('.csv', '').upper()
                
                for fila in lector:
                    if 'nombre' in fila and 'posicion' in fila and 'resistencia' in fila:
                        jugador = Jugador(
                            nombre=fila['nombre'],
                            posicion=fila['posicion'],
                            resistencia=fila['resistencia']
                        )
                        lista_jugadores.append(jugador)
                    else:
                        raise ValueError("CSV no tiene las columnas requeridas: nombre, posicion, resistencia.")

            if len(lista_jugadores) < 1:
                messagebox.showerror("Error de Carga", f"El archivo CSV para el Equipo {equipo_letra} no contiene jugadores válidos.")
                return

            nuevo_equipo = Equipo(nombre_equipo, lista_jugadores)

            if equipo_letra == "A":
                self.equipo_A = nuevo_equipo
                self.ruta_a.set(f"{nombre_equipo} | Jugadores: {len(lista_jugadores)}")
            else:
                self.equipo_B = nuevo_equipo
                self.ruta_b.set(f"{nombre_equipo} | Jugadores: {len(lista_jugadores)}")

            messagebox.showinfo("Carga Exitosa", f"Equipo {nombre_equipo} cargado con {len(lista_jugadores)} jugadores.")
            self.verificar_simulacion_disponible()

        except Exception as e:
            messagebox.showerror("Error de Carga", f"Ocurrió un error al cargar el archivo:\n{e}")
            if equipo_letra == "A":
                self.equipo_A = None
                self.ruta_a.set("[Cargar archivo CSV del Equipo A] - ERROR")
            else:
                self.equipo_B = None
                self.ruta_b.set("[Cargar archivo CSV del Equipo B] - ERROR")
            self.verificar_simulacion_disponible()

    def verificar_simulacion_disponible(self):
        """Habilita el botón de simulación si ambos equipos están cargados."""
        COLOR_CONTRASTE = "#FFC300"
        
        if self.equipo_A and self.equipo_B:
            self.btn_simular.config(state=tk.NORMAL, bg=COLOR_CONTRASTE, fg="black") 
            self.lbl_marcador.config(text=f"{self.equipo_A.nombre} 0 - 0 {self.equipo_B.nombre}")
        else:
            self.btn_simular.config(state=tk.DISABLED, bg="#9E9E9E", fg="white") 
            self.lbl_marcador.config(text="0 - 0")


    def ejecutar_simulacion(self):
        """Inicia el motor de simulación y muestra los resultados."""
        if not self.equipo_A or not self.equipo_B:
            messagebox.showwarning("Advertencia", "Debes cargar ambos equipos antes de simular.")
            return

        self.txt_reporte.delete(1.0, tk.END)
        COLOR_CONTRASTE = "#FFC300"
        self.lbl_marcador.config(fg=COLOR_CONTRASTE) 

        try:
            simulador = SimuladorPartido(self.equipo_A, self.equipo_B)
            log_minuto_a_minuto, eventos = simulador.simular()

            for linea in log_minuto_a_minuto:
                self.txt_reporte.insert(tk.END, linea + "\n")
            
            eq_a_final = simulador.eq_a
            eq_b_final = simulador.eq_b

            marcador_final = f"{eq_a_final.nombre} {eq_a_final.goles} - {eq_b_final.goles} {eq_b_final.nombre}"
            self.lbl_marcador.config(text=marcador_final, fg="#FFFFFF") 
            
            resumen = f"RESULTADO FINAL:\n{marcador_final}\n\nEventos Clave:\n" + "\n".join(eventos)
            messagebox.showinfo("Partido Terminado", resumen)

        except Exception as e:
            messagebox.showerror("Error de Simulación", f"Falló el motor de simulación:\n{e}")

# ------------------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# ------------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazFutbol(root)
    root.mainloop()
