import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import csv
import random

# ------------------------------------------------------------------
# MODELO (Lógica de Negocio)
# ------------------------------------------------------------------

class Jugador:
    def __init__(self, nombre, posicion, resistencia):
        self.nombre = nombre
        self.posicion = posicion
        self.resistencia = int(resistencia)
        self.resistencia_max = int(resistencia)
        
        # CORRECCIÓN 2: Definir perfil ofensivo/defensivo según posición
        if posicion.lower() in ["portero", "defensa"]:
            self.defensa = 0.8
            self.ataque = 0.2
        elif posicion.lower() == "mediocampista":
            self.defensa = 0.5
            self.ataque = 0.5
        elif posicion.lower() == "delantero":
            self.defensa = 0.2
            self.ataque = 0.8
        else:
            # Valor por defecto si hay error de tipeo
            self.defensa = 0.5
            self.ataque = 0.5

    def cansar(self, cantidad):
        self.resistencia -= cantidad
        if self.resistencia < 0: self.resistencia = 0

class Equipo:
    def __init__(self, nombre_equipo, lista_jugadores):
        self.nombre = nombre_equipo
        self.goles = 0
        
        # Separar titulares (primeros 11) y banca (el resto)
        if len(lista_jugadores) >= 11:
            self.titulares = lista_jugadores[:11]
            self.banca = lista_jugadores[11:]
        else:
            # Caso de emergencia si el CSV tiene pocos datos
            self.titulares = lista_jugadores
            self.banca = []
            
        self.cambios_realizados = 0
        self.tactica_actual = "Neutro" 

    def calcular_tactica(self):
        """
        CORRECCIÓN 2: La táctica depende de los jugadores en cancha.
        Sumamos los atributos de ataque y defensa de los 11 titulares.
        """
        total_ataque = sum(j.ataque for j in self.titulares)
        total_defensa = sum(j.defensa for j in self.titulares)
        
        if total_ataque > total_defensa + 1: # Margen para no oscilar tanto
            self.tactica_actual = "OFENSIVA"
        elif total_defensa > total_ataque + 1:
            self.tactica_actual = "DEFENSIVA"
        else:
            self.tactica_actual = "EQUILIBRADA"
            
        return total_ataque, total_defensa

    def verificar_cambios(self, minuto):
        """
        MEJORA 2.c: La resistencia es factor de decisión para cambios.
        Si un jugador tiene < 30% de resistencia, pide cambio.
        """
        mensajes = []
        if self.cambios_realizados >= 5: # Supongamos límite de 5 cambios
            return mensajes

        for i, jugador in enumerate(self.titulares):
            # Si el jugador está muy cansado (menos del 30% de su inicial)
            if jugador.resistencia < (jugador.resistencia_max * 0.3) and self.banca:
                
                # Buscar un reemplazo adecuado en la banca (misma posición preferiblemente)
                reemplazo = None
                for suplente in self.banca:
                    if suplente.posicion == jugador.posicion:
                        reemplazo = suplente
                        break
                
                # Si no hay de la misma posición, toma el primero que haya
                if not reemplazo and self.banca:
                    reemplazo = self.banca[0]
                
                if reemplazo:
                    # Ejecutar cambio
                    self.titulares[i] = reemplazo
                    self.banca.remove(reemplazo)
                    self.cambios_realizados += 1
                    
                    # Log del evento
                    mensajes.append(f"🔄 CAMBIO en {self.nombre} al min {minuto}: "
                                    f"Sale {jugador.nombre} ({jugador.posicion}) cansado, "
                                    f"Entra {reemplazo.nombre} ({reemplazo.posicion}).")
                    
                    if self.cambios_realizados >= 5:
                        break
        return mensajes

# ------------------------------------------------------------------
# MOTOR DE SIMULACIÓN
# ------------------------------------------------------------------

class SimuladorPartido:
    def __init__(self, equipo_a, equipo_b):
        self.eq_a = equipo_a
        self.eq_b = equipo_b
        self.log = [] # Aquí guardamos el minuto a minuto
        self.eventos_clave = [] # Goles y resumen final

    def simular(self):
        self.log.append(f"--- INICIO DEL PARTIDO: {self.eq_a.nombre} vs {self.eq_b.nombre} ---")
        
        # CORRECCIÓN 3: Ciclo Minuto a Minuto
        for minuto in range(1, 91):
            
            # 1. Calcular tácticas actuales
            atq_a, def_a = self.eq_a.calcular_tactica()
            atq_b, def_b = self.eq_b.calcular_tactica()
            
            # 2. Verificar cambios por cansancio
            msgs_a = self.eq_a.verificar_cambios(minuto)
            msgs_b = self.eq_b.verificar_cambios(minuto)
            for m in msgs_a + msgs_b:
                self.log.append(m)
                self.eventos_clave.append(m)

            # 3. Probabilidad de Gol
            # La probabilidad depende de (Mi Ataque vs Defensa Rival)
            # Factor base muy bajo porque es por minuto
            prob_gol_a = (atq_a / (def_b + 0.1)) * 0.015 
            prob_gol_b = (atq_b / (def_a + 0.1)) * 0.015

            # Intento de gol A
            if random.random() < prob_gol_a:
                autor = random.choice(self.eq_a.titulares)
                self.eq_a.goles += 1
                msg = f"⚽ ¡GOOOL de {self.eq_a.nombre}! (Min {minuto}) - {autor.nombre} ({autor.posicion})"
                self.log.append(msg)
                self.eventos_clave.append(msg)

            # Intento de gol B
            elif random.random() < prob_gol_b:
                autor = random.choice(self.eq_b.titulares)
                self.eq_b.goles += 1
                msg = f"⚽ ¡GOOOL de {self.eq_b.nombre}! (Min {minuto}) - {autor.nombre} ({autor.posicion})"
                self.log.append(msg)
                self.eventos_clave.append(msg)
            
            # 4. Desgaste de jugadores (reducir resistencia)
            # Si el equipo es OFENSIVO, se cansan más rápido
            factor_cansancio_a = 1.2 if self.eq_a.tactica_actual == "OFENSIVA" else 0.8
            factor_cansancio_b = 1.2 if self.eq_b.tactica_actual == "OFENSIVA" else 0.8

            for j in self.eq_a.titulares: j.cansar(random.uniform(0.5, 1.5) * factor_cansancio_a)
            for j in self.eq_b.titulares: j.cansar(random.uniform(0.5, 1.5) * factor_cansancio_b)

            # Log discreto de táctica (opcional, para no llenar pantalla)
            if minuto % 15 == 0:
                self.log.append(f"⏱ Min {minuto} | Tácticas -> {self.eq_a.nombre}: {self.eq_a.tactica_actual} vs {self.eq_b.nombre}: {self.eq_b.tactica_actual}")

        self.log.append("--- FIN DEL PARTIDO ---")
        return self.log, self.eventos_clave

# ------------------------------------------------------------------
# INTERFAZ GRÁFICA (GUI) - MEJORA 1 y 3
# ------------------------------------------------------------------

class InterfazFutbol:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Partido Táctico v2.0")
        self.root.geometry("700x600")

        # Variables para rutas de archivos
        self.ruta_a = tk.StringVar()
        self.ruta_b = tk.StringVar()

        # --- SECCIÓN DE CARGA ---
        frame_carga = tk.LabelFrame(root, text="Carga de Equipos (CSV)", padx=10, pady=10)
        frame_carga.pack(fill="x", padx=10, pady=5)

        tk.Button(frame_carga, text="Cargar Equipo A", command=lambda: self.cargar_csv("A")).grid(row=0, column=0, padx=5)
        tk.Label(frame_carga, textvariable=self.ruta_a).grid(row=0, column=1)

        tk.Button(frame_carga, text="Cargar Equipo B", command=lambda: self.cargar_csv("B")).grid(row=1, column=0, padx=5)
        tk.Label(frame_carga, textvariable=self.ruta_b).grid(row=1, column=1)

        self.btn_simular = tk.Button(root, text="⚽ JUGAR PARTIDO ⚽", command=self.ejecutar_simulacion, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        self.btn_simular.pack(pady=10)

        # --- SECCIÓN DE RESULTADOS ---
        frame_res = tk.Frame(root)
        frame_res.pack(fill="both", expand=True, padx=10)

        # Marcador
        self.lbl_marcador = tk.Label(frame_res, text="0 - 0", font=("Arial", 24, "bold"))
        self.lbl_marcador.pack()

        # Area de texto para el Minuto a Minuto
        tk.Label(frame_res, text="Reporte Minuto a Minuto:").pack(anchor="w")
        self.txt_reporte = scrolledtext.ScrolledText(frame_res, height=15)
        self.txt_reporte.pack(fill="both", expand=True)

        # Datos en memoria
        self.jugadores_a = []
        self.jugadores_b = []
        self.nombre_a = "Equipo A"
        self.nombre_b = "Equipo B"

    def cargar_csv(self, equipo_id):
        filepath = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv")])
        if not filepath: return

        try:
            lista_temp = []
            nombre_equipo = "Equipo Desconocido"
            
            with open(filepath, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                # Intenta obtener el nombre del archivo como nombre del equipo
                nombre_equipo = filepath.split("/")[-1].replace(".csv", "")
                
                for row in reader:
                    # Validar que existan las columnas
                    j = Jugador(row['Nombre'], row['Posicion'], row['Resistencia'])
                    lista_temp.append(j)
            
            if equipo_id == "A":
                self.ruta_a.set(nombre_equipo)
                self.jugadores_a = lista_temp
                self.nombre_a = nombre_equipo
            else:
                self.ruta_b.set(nombre_equipo)
                self.jugadores_b = lista_temp
                self.nombre_b = nombre_equipo
                
            messagebox.showinfo("Éxito", f"Se cargaron {len(lista_temp)} jugadores para {nombre_equipo}.")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo CSV.\nVerifica que tenga columnas: Nombre,Posicion,Resistencia.\nError: {e}")

    def ejecutar_simulacion(self):
        if not self.jugadores_a or not self.jugadores_b:
            messagebox.showwarning("Atención", "Debes cargar ambos archivos CSV antes de jugar.")
            return

        # Crear instancias de Equipos
        # (Importante: creamos copias nuevas para que la resistencia se resetee si jugamos de nuevo)
        import copy
        eq_a = Equipo(self.nombre_a, copy.deepcopy(self.jugadores_a))
        eq_b = Equipo(self.nombre_b, copy.deepcopy(self.jugadores_b))

        # Iniciar Simulador
        sim = SimuladorPartido(eq_a, eq_b)
        log_completo, eventos = sim.simular()

        # Mostrar Resultados en GUI
        self.lbl_marcador.config(text=f"{eq_a.nombre} {eq_a.goles} - {eq_b.goles} {eq_b.nombre}")
        
        self.txt_reporte.delete(1.0, tk.END)
        for linea in log_completo:
            self.txt_reporte.insert(tk.END, linea + "\n")
            # Resaltar goles en el texto (opcional y básico)
            if "GOOOL" in linea:
                self.txt_reporte.tag_add("gol", "end-2l", "end-1l")
                self.txt_reporte.tag_config("gol", foreground="red", font=("Arial", 10, "bold"))

        messagebox.showinfo("Partido Finalizado", f"Marcador Final:\n{eq_a.nombre}: {eq_a.goles}\n{eq_b.nombre}: {eq_b.goles}")

# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazFutbol(root)
    root.mainloop()