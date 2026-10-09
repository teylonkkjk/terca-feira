import tkinter as tk
import math
import random

class TerminalUI:
    def __init__(self, assistant_name="Terça Feira"):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        
        # Dimensões ampliadas para um visual de painel de controle
        self.width = 1100
        self.height = 650
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.eval('tk::PlaceWindow . center')
        
        # Transparência do holograma ajustada para melhor contraste
        self.root.attributes("-alpha", 0.92)

        # Paleta de Cores Cyberpunk/Sci-Fi Premium
        self.bg_color = "#000305"          # Fundo abismo profundo
        self.color_grid = "#01121a"        # Grade de fundo tática sutil
        self.color_idle = "#007a99"        # Azul tecnológico (Repouso)
        self.color_active = "#00ffff"      # Ciano brilhante puro (Ativa)
        self.color_processing = "#ff0055"  # Rosa Choque/Neon (Pensando)
        self.color_terminal = "#b3e6ff"    # Azul clarinho legível
        self.color_alert = "#ffbb00"       # Amarelo alerta

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.cx, self.cy = self.width // 2, self.height // 2 + 30
        
        # ---------------------------------------------------------
        # ARTE ESTÁTICA: Grade Holográfica de Fundo
        # ---------------------------------------------------------
        for x in range(0, self.width, 40):
            self.canvas.create_line(x, 0, x, self.height, fill=self.color_grid, dash=(2, 4))
        for y in range(0, self.height, 40):
            self.canvas.create_line(0, y, self.width, y, fill=self.color_grid, dash=(2, 4))

        # ---------------------------------------------------------
        # MOLDURA PRINCIPAL (Sci-Fi HUD Frame)
        # ---------------------------------------------------------
        frame_points = [
            40, 20, 
            self.width - 40, 20, 
            self.width - 15, 45, 
            self.width - 15, self.height - 45,
            self.width - 40, self.height - 20, 
            40, self.height - 20, 
            15, self.height - 45, 
            15, 45
        ]
        self.canvas.create_polygon(frame_points, outline=self.color_idle, fill="", width=2)
        # Detalhes de ancoragem (cantos brilhantes)
        self.canvas.create_line(15, 45, 40, 20, fill=self.color_active, width=4)
        self.canvas.create_line(self.width - 15, self.height - 45, self.width - 40, self.height - 20, fill=self.color_active, width=4)
        self.canvas.create_line(15, self.height - 45, 40, self.height - 20, fill=self.color_idle, width=4)
        self.canvas.create_line(self.width - 15, 45, self.width - 40, 20, fill=self.color_idle, width=4)

        # ---------------------------------------------------------
        # IDENTIDADE: HEADER DA TERÇA FEIRA
        # ---------------------------------------------------------
        self.canvas.create_text(self.width // 2, 45, text="T E R Ç A   F E I R A", fill=self.color_active, font=("Consolas", 26, "bold"))
        self.canvas.create_text(self.width // 2, 75, text="S.I.S.T.E.M.A  C.O.G.N.I.T.I.V.O  //  V 4.0", fill=self.color_idle, font=("Consolas", 9, "bold"))
        self.canvas.create_line(self.width//2 - 250, 95, self.width//2 + 250, 95, fill=self.color_idle, width=1, dash=(10, 5, 2, 5))

        # ---------------------------------------------------------
        # NÚCLEO DINÂMICO (The Core)
        # ---------------------------------------------------------
        # Radar Base Periférico
        self.canvas.create_oval(self.cx-210, self.cy-210, self.cx+210, self.cy+210, outline=self.color_grid, width=1, dash=(1, 5))
        
        # Hexágono de contenção (Glow fake)
        self.hex_glow = self.canvas.create_polygon(*self.get_polygon_points(6, 125, 0), outline=self.color_grid, fill="", width=8)
        self.hexagon = self.canvas.create_polygon(*self.get_polygon_points(6, 120, 0), outline=self.color_idle, fill="", width=2)
        
        # Triângulo interno
        self.triangle = self.canvas.create_polygon(*self.get_polygon_points(3, 80, 0), outline=self.color_idle, fill="", width=3)
        
        # Anéis rotativos de aceleração
        self.arc_fast = self.canvas.create_arc(self.cx-150, self.cy-150, self.cx+150, self.cy+150, 
                                               start=0, extent=140, outline=self.color_active, width=3, dash=(5, 10), style=tk.ARC)
        
        self.arc_slow = self.canvas.create_arc(self.cx-190, self.cy-190, self.cx+190, self.cy+190, 
                                               start=90, extent=250, outline=self.color_idle, width=1, dash=(40, 20), style=tk.ARC)

        # Nodos orbitais satélites
        self.orbit_nodes = []
        for _ in range(3):
            node = self.canvas.create_oval(0, 0, 0, 0, fill=self.color_active, outline="")
            self.orbit_nodes.append(node)

        # Texto Central Dinâmico
        self.center_text = self.canvas.create_text(self.cx, self.cy, text="STANDBY", fill=self.color_idle, font=("Consolas", 15, "bold", "italic"))

        # ---------------------------------------------------------
        # AUDIO VISUALIZER 360º (J.A.R.V.I.S Style)
        # ---------------------------------------------------------
        self.audio_lines = []
        self.num_audio_lines = 45  # Resolução do anel de áudio
        for _ in range(self.num_audio_lines):
            line = self.canvas.create_line(0, 0, 0, 0, fill=self.color_idle, width=2)
            self.audio_lines.append(line)

        # ---------------------------------------------------------
        # TERMINAL DE DADOS COM SCANNER (Lado Esquerdo)
        # ---------------------------------------------------------
        self.tx, self.ty, self.tw, self.th = 30, 250, 320, 280
        
        # Moldura Holográfica
        self.canvas.create_rectangle(self.tx, self.ty, self.tx+self.tw, self.ty+self.th, outline=self.color_idle, width=1)
        self.canvas.create_rectangle(self.tx, self.ty, self.tx+self.tw, self.ty+25, fill=self.color_idle, outline="")
        self.canvas.create_text(self.tx + 10, self.ty + 12, text="DATA STREAM //", fill="#000", font=("Consolas", 10, "bold"), anchor="w")
        
        self.text_area = tk.Text(
            self.root, bg=self.bg_color, fg=self.color_terminal, 
            font=("Consolas", 10), state=tk.DISABLED, wrap=tk.WORD,
            insertbackground="white", bd=0, highlightthickness=0, relief="flat"
        )
        self.text_area.place(x=self.tx+10, y=self.ty+35, width=self.tw-20, height=self.th-45)

        # Linha de escaneamento CRT sobre o terminal
        self.scanner_line = self.canvas.create_line(self.tx, self.ty+30, self.tx+self.tw, self.ty+30, fill=self.color_active, width=1)

        # ---------------------------------------------------------
        # TELEMETRIA AVANÇADA (Lado Direito)
        # ---------------------------------------------------------
        self.rx = self.width - 320
        self.canvas.create_text(self.rx, self.ty + 12, text="[ TELEMETRIA DO NÚCLEO ]", fill=self.color_active, font=("Consolas", 10, "bold"), anchor="w")
        self.telemetry_text = self.canvas.create_text(self.rx, self.ty + 40, text="", fill=self.color_idle, font=("Consolas", 9), justify="left", anchor="nw")

        # Dados Hexadecimais Decorativos descendo na direita
        self.matrix_text = self.canvas.create_text(self.rx + 220, self.ty + 40, text="", fill=self.color_idle, font=("Consolas", 8), justify="right", anchor="ne")

        # Variáveis de Engine Matemática e Física
        self.angle = 0.0
        self.pulse_phase = 0.0
        self.scanner_y = self.ty + 30
        self.scanner_dir = 1
        self.anim_state = "idle"
        
        self.canvas.bind("<ButtonPress-1>", self.iniciar_arrasto)
        self.canvas.bind("<B1-Motion>", self.arrastar_janela)

        self.root.withdraw()
        self.check_signals()
        self.animate_hud()

    # ==========================================
    # ENGINE MATEMÁTICA E RENDERIZAÇÃO
    # ==========================================
    def get_polygon_points(self, sides, radius, offset_angle):
        points = []
        for i in range(sides):
            angle = math.radians(offset_angle + (360 / sides) * i)
            x = self.cx + radius * math.cos(angle)
            y = self.cy + radius * math.sin(angle)
            points.extend([x, y])
        return points

    def update_telemetry(self):
        # Gera telemetria
        data = (
            f"SYS.CORE:  ESTÁVEL\n"
            f"MEMÓRIA:   0x{random.randint(1000, 9999):X}\n"
            f"PROCESS:   {random.randint(12, 89)}%\n"
            f"LATÊNCIA:  {random.randint(2, 45)}ms\n"
            f"CONEXÃO:   {random.choice(['CRIPTOGRAFADA', 'SEGURA', 'ATIVA'])}\n"
            f"-----------------------\n"
            f"T-RNG OUT: {random.random():.5f}\n"
            f"V-SEC OVR: {random.randint(0,1)}\n"
        )
        self.canvas.itemconfig(self.telemetry_text, text=data)
        
        # Gera chuva hexadecimal Matrix-style
        hex_rain = "\n".join([f"{random.randint(0, 255):02X} {random.randint(0, 255):02X}" for _ in range(12)])
        self.canvas.itemconfig(self.matrix_text, text=hex_rain)

    def update_audio_visualizer(self, is_speaking, color):
        """Mapeia as barras de áudio em um anel 360 graus ao redor do núcleo"""
        base_radius = 230
        for i, line in enumerate(self.audio_lines):
            # Adiciona a rotação global para as linhas girarem lentamente enquanto pulsam
            angle = math.radians(i * (360 / self.num_audio_lines) + (self.angle * 0.3))
            
            if is_speaking:
                h = random.randint(5, 40)
            else:
                # Efeito de respiração vital em standby
                h = 5 + (math.sin(self.pulse_phase * 2 + i) * 3)
                
            x1 = self.cx + base_radius * math.cos(angle)
            y1 = self.cy + base_radius * math.sin(angle)
            x2 = self.cx + (base_radius + h) * math.cos(angle)
            y2 = self.cy + (base_radius + h) * math.sin(angle)
            
            self.canvas.coords(line, x1, y1, x2, y2)
            self.canvas.itemconfig(line, fill=color)

    def animate_hud(self):
        velocidade = 1.0
        cor_atual = self.color_idle
        texto_central = "S T A N D B Y"
        is_speaking = False

        # Máquina de Estados Visual
        if self.anim_state == "listening":
            velocidade = 4.0
            cor_atual = self.color_active
            texto_central = "E S C U T A N D O"
        elif self.anim_state == "processing":
            velocidade = 12.0
            cor_atual = self.color_processing
            texto_central = "P R O C E S S A N D O"
        elif self.anim_state == "speaking":
            velocidade = 2.5
            cor_atual = self.color_active
            texto_central = "F A L A N D O"
            is_speaking = True

        # Atualiza Texto Central
        self.canvas.itemconfig(self.center_text, text=texto_central, fill=cor_atual)
        
        # Matemática de Animação (Removida a trava de 360 graus que causava o "pulo")
        self.angle += velocidade
        self.pulse_phase += 0.05
        
        # Efeito de "Respiração" Orgânica da IA (Pulsating Radius)
        pulse = math.sin(self.pulse_phase) * 5 
        
        # Renderização Geométrica Contínua
        self.canvas.coords(self.hexagon, *self.get_polygon_points(6, 120 + pulse, self.angle * 0.8))
        self.canvas.coords(self.hex_glow, *self.get_polygon_points(6, 125 + pulse, self.angle * 0.8))
        self.canvas.coords(self.triangle, *self.get_polygon_points(3, 80 - pulse, -self.angle * 1.5))
        
        self.canvas.itemconfig(self.hexagon, outline=cor_atual)
        self.canvas.itemconfig(self.triangle, outline=cor_atual)

        # Renderização dos Anéis
        self.canvas.itemconfig(self.arc_fast, start=self.angle * 2, outline=cor_atual)
        self.canvas.itemconfig(self.arc_slow, start=-self.angle * 0.5)

        # Renderização dos Nodos Satélites Orbitais
        for i, node in enumerate(self.orbit_nodes):
            a = math.radians(self.angle * 1.2 + i * 120)
            r = 180 + math.sin(math.radians(self.angle * 3 + i)) * 15 # Órbita elíptica dinâmica
            nx, ny = self.cx + r * math.cos(a), self.cy + r * math.sin(a)
            self.canvas.coords(node, nx-4, ny-4, nx+4, ny+4)
            self.canvas.itemconfig(node, fill=cor_atual)

        # Animação do Scanner CRT do Terminal
        self.scanner_y += 2 * self.scanner_dir
        if self.scanner_y > self.ty + self.th - 10:
            self.scanner_dir = -1
        elif self.scanner_y < self.ty + 30:
            self.scanner_dir = 1
        self.canvas.coords(self.scanner_line, self.tx+2, self.scanner_y, self.tx+self.tw-2, self.scanner_y)

        # Telemetria reduzida para performance visual (6 frames)
        # Permite usar módulo (%) no angle casted para inteiro sem prejudicar a rotação real
        if int(self.angle) % 6 == 0:
            self.update_telemetry()
            
        # Áudio Visualizer 360º
        self.update_audio_visualizer(is_speaking, cor_atual)

        # Loop de 60 FPS (16ms)
        self.root.after(16, self.animate_hud)

    # ==========================================
    # LÓGICA DE INTERAÇÃO DO SISTEMA
    # ==========================================
   # ==========================================
    # LÓGICA DE INTERAÇÃO DO SISTEMA
    # ==========================================
    def log(self, message):
        # 1. Atualiza a Máquina de Estados Visual do HUD silenciosamente
        if "Aguardando comando" in message or "Ouvindo" in message:
            self.anim_state = "listening"
            return  # BLOQUEIA o spam de texto repetitivo na tela
            
        elif "Aguardando chamada" in message or "STANDBY" in message or "modo de espera" in message:
            self.anim_state = "idle"
            return  # BLOQUEIA o spam de standby na tela
            
        elif "Consultando rede neural" in message or "Transcrevendo" in message or "Processando" in message:
            self.anim_state = "processing"
            # Opcional: Se quiser que apareça que está a processar, remova o 'return'. 
            # Mas para manter limpo, deixamos o núcleo visual indicar.
            return 
            
        elif "Ruído ignorado" in message or "Alucinação" in message:
            return  # Descarta logs inúteis de estática do microfone

        # 2. Formatação para Ações Reais e Respostas (Aparecem apenas uma vez)
        if "Terça Feira:" in message or "[RESPOSTA IA]" in message or "\n[TERÇA FEIRA]" in message:
            self.anim_state = "speaking"
            message = message.replace('Terça Feira: ', '').replace('[RESPOSTA IA]', '').replace('[TERÇA FEIRA]', '')
            if message.strip():
                message = f"> {message.strip()}"
        elif "ONLINE" in message:
            self.anim_state = "idle"

        def _log():
            self.text_area.config(state=tk.NORMAL)
            if not message.startswith(">") and "[" in message:
                formatado = f"{message}\n"
            else:
                formatado = f"{message}\n\n"
                
            self.text_area.insert(tk.END, formatado)
            self.text_area.see(tk.END) 
            self.text_area.config(state=tk.DISABLED)
            
        self.root.after(0, _log)

    def iniciar_arrasto(self, event):
        self.x = event.x
        self.y = event.y

    def arrastar_janela(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def check_signals(self):
        self.root.after(100, self.check_signals)
        
    def clear(self):
        def _clear():
            self.text_area.config(state=tk.NORMAL)
            self.text_area.delete('1.0', tk.END)
            self.text_area.config(state=tk.DISABLED)
        self.root.after(0, _clear)
        
    def show(self):
        def _show():
            self.anim_state = "idle"
            self.root.deiconify()
            self.root.attributes('-topmost', True)
        self.root.after(0, _show)
        
    def hide(self):
        self.root.after(0, self.root.withdraw)
        
    def start(self):
        self.root.mainloop()