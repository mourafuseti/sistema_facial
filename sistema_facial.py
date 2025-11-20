# ====================================================================
# Sistema de Reconhecimento Facial com CustomTkinter e SQLite
#
# Autor: LEONARDO DE MOURA FUSETI
# GitHub: https://github.com/mourafuseti
# Data: Novembro de 2025 (ou a data da sua última modificação)
# Descrição: Sistema para controle de acesso utilizando webcam,
#            multithreading para estabilidade da GUI, registro
#            em banco de dados e gestão de Lista Negra.
# ====================================================================

import customtkinter as ctk
import cv2
import face_recognition
import os
import numpy as np
import sqlite3
from datetime import datetime
import time
import threading
from PIL import Image, ImageTk, ImageDraw 

# --- 1. Configuração do Sistema e Pastas ---
# -------------------------------------------------------------
AUTHORIZED_FACES_DIR = "faces_autorizadas"
BLACK_LIST_FACES_DIR = "lista_negra_faces"
UNAUTHORIZED_CAPTURES_DIR = "capturas_nao_autorizadas"
DATABASE_NAME = "controle_acesso.db"

# Cria as pastas se não existirem
os.makedirs(AUTHORIZED_FACES_DIR, exist_ok=True)
os.makedirs(BLACK_LIST_FACES_DIR, exist_ok=True)
os.makedirs(UNAUTHORIZED_CAPTURES_DIR, exist_ok=True)

# Variáveis de controle globais
is_running = False
known_encodings = []
known_names = []
is_black_list = []

# --- 2. Funções de Banco de Dados (SQLite) ---
# -------------------------------------------------------------

def setup_database():
    """Cria a tabela de registro de acessos se ela não existir."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS acessos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                data_hora TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        print("Banco de dados SQLite configurado.")
    except sqlite3.Error as e:
        print(f"Erro ao configurar o banco de dados: {e}")

def registrar_acesso(nome, status):
    """Registra um evento de acesso no DB."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO acessos (nome, data_hora, status) VALUES (?, ?, ?)",
                  (nome, agora, status))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Erro ao registrar acesso no DB: {e}")


# --- 3. Funções de Carregamento de Faces ---
# -------------------------------------------------------------

def carregar_faces():
    """Carrega as faces autorizadas e da lista negra."""
    global known_encodings, known_names, is_black_list
    known_encodings.clear()
    known_names.clear()
    is_black_list.clear()

    print("\n--- Carregando Faces ---")
    
    def load_from_dir(directory, is_banned):
        for filename in os.listdir(directory):
            if filename.endswith(('.jpg', '.png', '.jpeg')):
                name = os.path.splitext(filename)[0]
                filepath = os.path.join(directory, filename)
                try:
                    image = face_recognition.load_image_file(filepath)
                    encodings = face_recognition.face_encodings(image)
                    if encodings:
                        known_encodings.append(encodings[0])
                        known_names.append(name)
                        is_black_list.append(is_banned)
                        status_str = "Lista Negra 🔴" if is_banned else "Autorizada 🟢"
                        print(f"  - Face de '{name}' ({status_str}) carregada.")
                except Exception:
                    print(f"  - Erro ou nenhuma face em {filename}.")

    load_from_dir(AUTHORIZED_FACES_DIR, False)
    load_from_dir(BLACK_LIST_FACES_DIR, True)
    
    return len(known_encodings) > 0


# --- 4. Lógica de Reconhecimento Facial (Rodando em Thread) ---
# -------------------------------------------------------------

class VideoStreamThread(threading.Thread):
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance # Referência à instância principal da App
        self.stop_event = threading.Event()
        self.last_access_time = {} 
        self.MIN_REGISTRATION_INTERVAL = 5
        self.cap = cv2.VideoCapture(0)

    def run(self):
        global is_running
        is_running = True
        
        if not self.cap.isOpened():
            print("Erro: Câmera não pôde ser aberta.")
            is_running = False
            return

        print("Thread de processamento de vídeo iniciada.")
        
        frame_count = 0
        PROCESS_EVERY_N_FRAMES = 5 # Processa o reconhecimento a cada 5 frames

        while not self.stop_event.is_set():
            ret, frame = self.cap.read()
            if not ret: break
            
            # Inicializa variáveis para o loop de desenho
            face_locations = []
            current_names_statuses = []
            current_time = time.time()
            
            # Otimização: Só processa o reconhecimento em frames alternados
            if frame_count % PROCESS_EVERY_N_FRAMES == 0:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                
                for i, face_encoding in enumerate(face_encodings):
                    
                    name = "Desconhecido"
                    status = "Não Autorizado"
                    
                    # Compara a face detectada
                    if known_encodings:
                        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
                        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)
                        
                        if matches[best_match_index]:
                            name = known_names[best_match_index]
                            status = "Lista Negra" if is_black_list[best_match_index] else "Autorizado"
                            
                    current_names_statuses.append((name, status))
                    
                    # --- Lógica de Registro no DB ---
                    reg_name = name
                    
                    if status == "Autorizado":
                        if (name not in self.last_access_time) or (current_time - self.last_access_time[name] > self.MIN_REGISTRATION_INTERVAL):
                            registrar_acesso(name, status)
                            self.last_access_time[name] = current_time
                    
                    elif status == "Lista Negra":
                        reg_name = f"LISTA NEGRA - {name}"
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        capture_filename = f"{UNAUTHORIZED_CAPTURES_DIR}/{reg_name}_{timestamp}.jpg"
                        cv2.imwrite(capture_filename, frame)
                        registrar_acesso(reg_name, status)
                        
                    else: # Desconhecido
                        reg_name = "Desconhecido"
                        if (reg_name not in self.last_access_time) or (current_time - self.last_access_time[reg_name] > self.MIN_REGISTRATION_INTERVAL):
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            capture_filename = f"{UNAUTHORIZED_CAPTURES_DIR}/{reg_name}_{timestamp}.jpg"
                            cv2.imwrite(capture_filename, frame)
                            registrar_acesso(reg_name, status)
                            self.last_access_time[reg_name] = current_time

                # Armazena os resultados para o próximo frame
                self.app.last_face_locations = face_locations
                self.app.last_names_statuses = current_names_statuses

            # 2. Desenho do Frame (Usa os resultados mais recentes)
            frame = self.draw_boxes_on_frame(frame)

            # 3. Armazena o frame final para a GUI (Thread-Safe)
            self.app.current_frame = frame 
            
            frame_count += 1
            time.sleep(0.005) # Pequena pausa para ceder tempo

        # Limpeza
        self.cap.release()
        is_running = False
        print("Thread de vídeo encerrada.")

    def draw_boxes_on_frame(self, frame):
        """Função auxiliar para desenhar caixas e nomes no frame."""
        
        # Desenha caixas e nomes com base nos últimos resultados
        for face_location, (name, status) in zip(self.app.last_face_locations, self.app.last_names_statuses):
            
            # Cores BGR do OpenCV
            color = (0, 165, 255)  # Laranja (Desconhecido)
            display_text = "❓ DESCONHECIDO"
            
            if status == "Autorizado":
                color = (0, 255, 0) # Verde
                display_text = f"ACESSO: {name}"
            elif status == "Lista Negra":
                color = (0, 0, 255) # Vermelho
                display_text = f"🚨 PROIBIDO: {name}"
                
            # Redimensiona as localizações 4x para o frame original
            top, right, bottom, left = [c * 4 for c in face_location]
            
            # Desenha retângulo e texto
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, display_text, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

        return frame

    def stop(self):
        """Sinaliza para a thread parar."""
        self.stop_event.set()
        
        
# --- 5. Interface Gráfica (CustomTkinter) ---
# -------------------------------------------------------------

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Variáveis de estado para a thread de vídeo
        self.current_frame = None 
        self.video_thread = None
        self.last_face_locations = []
        self.last_names_statuses = []
        
        # Configuração básica da janela
        self.title("Controle de Acesso Facial - CTk")
        self.geometry("1000x600")
        self.grid_columnconfigure(0, weight=0) # Barra lateral
        self.grid_columnconfigure(1, weight=1) # Área principal
        self.grid_rowconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --------------------- BARRA LATERAL (MENU) ---------------------
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(self.sidebar_frame, text="FACIAL ACCESS", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.start_button = ctk.CTkButton(self.sidebar_frame, text="📸 INICIAR CÂMERA", command=self.start_recognition)
        self.start_button.grid(row=1, column=0, padx=20, pady=10)

        self.stop_button = ctk.CTkButton(self.sidebar_frame, text="⏹ PARAR CÂMERA", command=self.stop_recognition, state="disabled")
        self.stop_button.grid(row=2, column=0, padx=20, pady=10)

        ctk.CTkButton(self.sidebar_frame, text="📜 Ver Registros", command=self.show_records).grid(row=3, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar_frame, text="❓ Info Cadastro", command=self.show_info).grid(row=4, column=0, padx=20, pady=10)

        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="Status: Parado", text_color="red")
        self.status_label.grid(row=6, column=0, padx=20, pady=20, sticky="s")


        # --------------------- ÁREA PRINCIPAL (CÂMERA) ---------------------
        self.camera_frame = ctk.CTkFrame(self)
        self.camera_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.camera_frame.grid_columnconfigure(0, weight=1)
        self.camera_frame.grid_rowconfigure(0, weight=1)
        
        # Label para exibir o feed de vídeo
        self.camera_label = ctk.CTkLabel(self.camera_frame, text="Câmera Desligada\nClique em 'INICIAR CÂMERA'", fg_color="gray20", width=800, height=500)
        self.camera_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
    def start_recognition(self):
        """Inicia o carregamento de faces e a thread de vídeo."""
        if not is_running:
            if not carregar_faces():
                self.status_label.configure(text="Erro: Sem faces cadastradas!", text_color="yellow")
                return
            
            # Inicia a thread de vídeo
            self.video_thread = VideoStreamThread(self) # Passa 'self'
            self.video_thread.start()
            
            # Inicia o loop de atualização da GUI (self.after)
            self.update_gui_frame()
            
            # Atualiza a GUI
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.status_label.configure(text="Status: Ativo", text_color="green")
            print("Sistema iniciado com sucesso.")

    def stop_recognition(self):
        """Para a thread de vídeo e limpa a GUI."""
        global is_running
        if is_running and self.video_thread:
            self.video_thread.stop()
            self.video_thread.join()
            self.video_thread = None
            is_running = False
            
            # Atualiza a GUI
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.status_label.configure(text="Status: Parado", text_color="red")
            self.camera_label.configure(image=None, text="Câmera Desligada\nClique em 'INICIAR CÂMERA'")
            
            # Reinicia as variáveis de rastreamento de face
            self.last_face_locations = []
            self.last_names_statuses = []
            print("Sistema parado.")

    def update_gui_frame(self):
        """
        Função chamada repetidamente por 'self.after()' para atualizar o frame
        na thread principal da GUI. Isso resolve o travamento.
        """
        if is_running and self.current_frame is not None:
            # 1. Pega o frame processado
            frame = self.current_frame
            
            # 2. Conversão Otimizada para CustomTkinter
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            
            # Obtém o tamanho atual do label para redimensionar corretamente
            try:
                target_width = self.camera_label.winfo_width()
                target_height = self.camera_label.winfo_height()
                if target_width > 1 and target_height > 1:
                    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            except:
                 # Usa o tamanho padrão se a janela ainda não estiver mapeada
                 pass 
                 
            img_tk = ImageTk.PhotoImage(image=img)
            
            # Atualiza o Label da Câmera
            self.camera_label.configure(image=img_tk)
            self.camera_label.image = img_tk # Evita o garbage collection
            
            # Agenda a próxima atualização (30ms = ~33 FPS para a GUI)
            self.after(30, self.update_gui_frame) 
        
    def on_closing(self):
        """Garante que a thread de vídeo seja parada ao fechar a janela."""
        self.stop_recognition()
        self.destroy()

    # --- Funções de Menu ---
    
    def show_records(self):
        """Mostra os registros do DB em uma nova janela."""
        # Se estiver rodando, pausa a câmera (opcional, mas recomendado)
        was_running = is_running
        if was_running:
            self.stop_recognition() 
            
        record_window = ctk.CTkToplevel(self)
        record_window.title("Registros de Acesso")
        record_window.geometry("600x400")
        
        ctk.CTkLabel(record_window, text="Últimos Registros de Acesso", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        # Lógica para pegar registros do DB
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            c = conn.cursor()
            c.execute("SELECT nome, data_hora, status FROM acessos ORDER BY id DESC LIMIT 20")
            registros = c.fetchall()
            conn.close()
        except sqlite3.Error:
            registros = []
        
        if registros:
            text_output = "DATA/HORA\t\tNOME\t\tSTATUS\n" + ("-"*60) + "\n"
            for nome, data_hora, status in registros:
                text_output += f"{data_hora}\t{nome:<15}\t{status}\n"
        else:
            text_output = "Nenhum registro encontrado."
            
        record_box = ctk.CTkTextbox(record_window, width=580, height=300)
        record_box.insert("0.0", text_output)
        record_box.configure(state="disabled")
        record_box.pack(padx=10, pady=10)
        
        # Função para retomar a câmera ao fechar a janela de registro
        def on_record_close():
            if was_running:
                self.start_recognition()
            record_window.destroy()
            
        record_window.protocol("WM_DELETE_WINDOW", on_record_close)
        
    def show_info(self):
        """Mostra informações de cadastro."""
        info_window = ctk.CTkToplevel(self)
        info_window.title("Instruções de Cadastro")
        info_window.geometry("500x350")
        
        text = (
            "Para cadastrar faces, utilize as pastas:\n\n"
            f"1. **PESSOAS AUTORIZADAS** (Acesso Liberado):\n"
            f"   - Pasta: '{AUTHORIZED_FACES_DIR}'\n\n"
            f"2. **LISTA NEGRA** (Acesso Proibido/Alerta):\n"
            f"   - Pasta: '{BLACK_LIST_FACES_DIR}'\n\n"
            "**Regra:** O nome do arquivo (ex: 'joao.jpg') será o nome da pessoa no sistema.\n"
            "Certifique-se de que a imagem contém apenas um rosto claro."
        )
        
        ctk.CTkLabel(info_window, text="Instruções de Cadastro", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        info_box = ctk.CTkTextbox(info_window, width=480, height=250)
        info_box.insert("0.0", text)
        info_box.configure(state="disabled")
        info_box.pack(padx=10, pady=5)


if __name__ == "__main__":
    setup_database()
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue") 
    
    app = App()
    app.mainloop()