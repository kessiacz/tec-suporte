import customtkinter as ctk
import psutil
import os
import subprocess
import threading
import sys
import ctypes
import platform
from datetime import datetime

# Configurações Iniciais
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class SuporteTecnicoGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SISTEMA DE SUPORTE E MONITORAMENTO")
        self.geometry("1100x750")

        # Configuração de Grid Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR VERTICAL ---
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="SISTEMA DE SUPORTE", font=ctk.CTkFont(size=18, weight="bold"))
        self.logo_label.pack(pady=(20, 10))

        # Menu Scroll
        self.scroll_menu = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.scroll_menu.pack(expand=True, fill="both", padx=5, pady=5)

        self.setup_menu_vertical()

        # --- SEÇÃO DE TEMA ---
        self.tema_label = ctk.CTkLabel(self.sidebar, text="Aparência:", font=ctk.CTkFont(size=12))
        self.tema_label.pack(pady=(10, 0))
        
        self.tema_option = ctk.CTkOptionMenu(
            self.sidebar, 
            values=["System", "Dark", "Light"], 
            command=self.mudar_tema
        )
        self.tema_option.pack(pady=(5, 20), padx=20)

        # --- ÁREA CENTRAL ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure((0, 1), weight=1)

        self.label_monitor = ctk.CTkLabel(self.main_frame, text="MONITORAMENTO EM TEMPO REAL", font=ctk.CTkFont(size=16, weight="bold"))
        self.label_monitor.grid(row=0, column=0, columnspan=2, pady=(10, 5))

        self.cpu_card = self.criar_card("USO DE CPU", "0%", 1, 0)
        self.ram_card = self.criar_card("USO DE RAM", "0%", 1, 1)
        
        self.log_text = ctk.CTkTextbox(self.main_frame, corner_radius=10, border_width=1)
        self.log_text.grid(row=3, column=0, columnspan=2, padx=20, pady=(20, 20), sticky="nsew")
        self.main_frame.grid_rowconfigure(3, weight=1)

        self.atualizar_dados()

    def criar_label_grupo(self, texto):
        label = ctk.CTkLabel(self.scroll_menu, text=texto, font=ctk.CTkFont(size=13, weight="bold"), text_color="#3b8ed0")
        label.pack(pady=(15, 5), anchor="w", padx=10)

    def setup_menu_vertical(self):
        # GRUPO MANUTENÇÃO
        self.criar_label_grupo("MANUTENÇÃO")
        ctk.CTkButton(self.scroll_menu, text="Limpar Temp", command=self.limpar_temp).pack(pady=2, fill="x", padx=10)
        ctk.CTkButton(self.scroll_menu, text="Limpar DNS", command=lambda: self.executar_cmd("ipconfig /flushdns")).pack(pady=2, fill="x", padx=10)
        ctk.CTkButton(self.scroll_menu, text="Resetar Rede", command=self.resetar_rede).pack(pady=2, fill="x", padx=10)

        # GRUPO SISTEMA
        self.criar_label_grupo("SISTEMA")
        ctk.CTkButton(self.scroll_menu, text="Ver Rede (IP)", command=lambda: self.executar_cmd("ipconfig /all")).pack(pady=2, fill="x", padx=10)
        ctk.CTkButton(self.scroll_menu, text="Info Sistema", command=lambda: self.executar_cmd("systeminfo")).pack(pady=2, fill="x", padx=10)
        ctk.CTkButton(self.scroll_menu, text="SFC Scannow", command=lambda: self.executar_cmd("sfc /scannow")).pack(pady=2, fill="x", padx=10)
        ctk.CTkButton(self.scroll_menu, text="CHKDSK", command=lambda: self.executar_cmd("chkdsk")).pack(pady=2, fill="x", padx=10)
        ctk.CTkButton(self.scroll_menu, text="DISM Repair", command=lambda: self.executar_cmd("DISM /Online /Cleanup-Image /RestoreHealth")).pack(pady=2, fill="x", padx=10)

        # GRUPO REDE
        self.criar_label_grupo("REDE")
        ctk.CTkButton(self.scroll_menu, text="Testar Conexão", command=self.testar_conexao).pack(pady=2, fill="x", padx=10)
        ctk.CTkButton(self.scroll_menu, text="Portas Abertas", command=lambda: self.executar_cmd("netstat -ano")).pack(pady=2, fill="x", padx=10)
        ctk.CTkButton(self.scroll_menu, text="Wi-Fi Perfis", command=lambda: self.executar_cmd("netsh wlan show profiles")).pack(pady=2, fill="x", padx=10)

        # GRUPO PROCESSOS
        self.criar_label_grupo("PROCESSOS")
        ctk.CTkButton(self.scroll_menu, text="Ver Processos", command=lambda: self.executar_cmd("tasklist")).pack(pady=2, fill="x", padx=10)
        ctk.CTkButton(self.scroll_menu, text="Usuário Atual", command=lambda: self.executar_cmd("whoami")).pack(pady=2, fill="x", padx=10)

        # GRUPO DIAGNÓSTICO
        self.criar_label_grupo("DIAGNÓSTICO")
        ctk.CTkButton(self.scroll_menu, text="Diag. Completo", command=self.diagnostico_real).pack(pady=2, fill="x", padx=10)
        ctk.CTkButton(self.scroll_menu, text="Verificar Drivers", command=self.verificar_drivers).pack(pady=2, fill="x", padx=10)
        ctk.CTkButton(self.scroll_menu, text="Gerar Relatório", command=self.gerar_relatorio).pack(pady=2, fill="x", padx=10)

    def mudar_tema(self, novo_tema):
        ctk.set_appearance_mode(novo_tema)
        self.log(f"Tema alterado para: {novo_tema}")

    def criar_card(self, titulo, valor_inicial, row, col):
        frame = ctk.CTkFrame(self.main_frame, fg_color=("gray85", "gray15"))
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(frame, text=titulo, font=ctk.CTkFont(size=12)).pack(pady=(10, 0))
        lbl_valor = ctk.CTkLabel(frame, text=valor_inicial, font=ctk.CTkFont(size=24, weight="bold"), text_color="#3b8ed0")
        lbl_valor.pack(pady=(0, 10))
        return lbl_valor

    # --- LÓGICA DE FUNCIONAMENTO ---
    def atualizar_dados(self):
        try:
            self.cpu_card.configure(text=f"{psutil.cpu_percent()}%")
            self.ram_card.configure(text=f"{psutil.virtual_memory().percent}%")
        except: pass
        self.after(1000, self.atualizar_dados)

    def log(self, mensagem):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{ts}] {mensagem}\n")
        self.log_text.see("end")

    def executar_cmd(self, comando):
        def run():
            self.log(f"Executando: {comando}")
            subprocess.run(f'start cmd /k "{comando}"', shell=True)
        threading.Thread(target=run).start()

    def limpar_temp(self):
        def run():
            self.log("Iniciando limpeza de temporários...")
            os.system("del /q/f/s %TEMP%\\* >nul 2>&1")
            self.log("Limpeza concluída.")
        threading.Thread(target=run).start()

    def resetar_rede(self):
        def run():
            self.log("Resetando rede...")
            cmds = ["netsh winsock reset", "netsh int ip reset", "ipconfig /release", "ipconfig /renew"]
            for c in cmds: subprocess.run(c, shell=True, capture_output=True)
            self.log("Rede resetada.")
        threading.Thread(target=run).start()

    def testar_conexao(self):
        res = subprocess.run("ping -n 1 8.8.8.8", shell=True, capture_output=True)
        self.log("Status: ONLINE" if res.returncode == 0 else "Status: OFFLINE")

    def verificar_drivers(self):
        res = subprocess.run('wmic path Win32_PnPEntity where "ConfigManagerErrorCode != 0" get Name', shell=True, capture_output=True, text=True)
        self.log(f"Drivers com erro:\n{res.stdout.strip()}" if res.stdout.strip() else "Todos os drivers OK.")

    def diagnostico_real(self):
        self.log("--- INICIANDO DIAGNÓSTICO ---")
        self.log(f"Processador: {platform.processor()}")
        self.log(f"SO: {platform.system()} {platform.release()}")
        self.testar_conexao()

    def gerar_relatorio(self):
        nome_arq = "Relatorio_Tecnico.txt"
        with open(nome_arq, "w") as f:
            f.write(f"Relatório de Suporte - {datetime.now()}\n")
            f.write(f"Máquina: {platform.node()}\n")
            f.write("-" * 30 + "\n")
            subprocess.run("systeminfo", shell=True, stdout=f)
        self.log(f"Relatório salvo como {nome_arq}")

# =========================
# INICIALIZAÇÃO COMO ADMIN
# =========================
def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

if __name__ == "__main__":
    if is_admin():
        app = SuporteTecnicoGUI()
        app.mainloop()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)