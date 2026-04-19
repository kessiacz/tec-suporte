import customtkinter as ctk
import psutil
import os
import subprocess
import threading
import sys
import ctypes
import platform
import re
from datetime import datetime

# CONFIGURAÇÃO DE APARÊNCIA
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class SuporteTecnicoGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SISTEMA DE SUPORTE")
        largura_janela = 1100
        altura_janela = 500

        self.centralizar_janela(largura_janela, altura_janela)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.menu_hover = None
        self.ultimo_grupo_clicado = None

        # ================= MENU SUPERIOR =================
        self.barra_superior = ctk.CTkFrame(self, height=50, corner_radius=0)
        self.barra_superior.grid(row=0, column=0, sticky="ew")

        self.tema_option = ctk.CTkOptionMenu(
            self.barra_superior, 
            values=["System", "Dark", "Light"], 
            command= self.mudar_tema,
            width=100,
            fg_color=("gray80", "gray25"),
            button_color=("gray70", "gray30"),
            button_hover_color=("gray60", "gray40"),
            text_color=("black", "white")
        )
        self.tema_option.pack(side="right", padx=15, pady=5)

        # ================= MAIN FRAME =================
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=3)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # MONITORAMENTO
        self.monitor_frame = ctk.CTkFrame(self.main_frame)
        self.monitor_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.centros_labels = ctk.CTkFrame(self.monitor_frame, fg_color="transparent")
        self.centros_labels.place(relx=0.5, rely=0.5, anchor="center")

        self.cpu_label = ctk.CTkLabel(self.centros_labels, text="CPU: 0%", font=ctk.CTkFont(size=22, weight="bold"))
        self.cpu_label.pack(pady=10)
        self.ram_label = ctk.CTkLabel(self.centros_labels, text="RAM: 0%", font=ctk.CTkFont(size=22, weight="bold"))
        self.ram_label.pack(pady=10)

        # LOGS
        self.log_frame = ctk.CTkFrame(self.main_frame)
        self.log_frame.grid(row=0, column=1, sticky="nsew")
        self.log_text = ctk.CTkTextbox(self.log_frame, font=("Consolas", 12), text_color=("black", "white"), fg_color=("white", "gray15"))
        self.log_text.pack(expand=True, fill="both", padx=10, pady=10)

        self.bind("<Button-1>", self.clique_fora)

        self.definir_menus()
        self.criar_botoes_topo()
        self.atualizar_dados()


    def centralizar_janela(self, largura, altura):
        tela_largura = self.winfo_screenwidth()
        tela_altura = self.winfo_screenheight()

        x = (tela_largura // 2) - (largura // 2)
        y = (tela_altura // 2) - (altura // 2)

        self.geometry(f"{largura}x{altura}+{x}+{y}")

    def definir_menus(self):
        self.menus_data = {
            "REDE": [
                ("Status de Conexão", self.verificar_conectividade),
                ("Redes Wi-Fi Salvas", self.listar_redes_wifi),
                ("IP / Mac / DNS", lambda: self.executar_cmd("ipconfig /all")),
                ("Flush DNS", lambda: self.executar_cmd("ipconfig /flushdns")),
                ("Renovação de IP", self.renovar_ip),
                ("NTP (ntp.br)", self.sincronizar_ntp),
                ("Traceroute", lambda: self.executar_cmd("tracert 8.8.8.8"))
            ],
            "SISTEMA": [
                ("Limpeza Temp", self.limpar_temp),
                ("Limpeza de Disco", self.limpeza_completa),
                ("SFC Scan", lambda: self.executar_cmd("sfc /scannow")),
                ("DISM Check", lambda: self.executar_cmd("DISM /Online /Cleanup-Image /RestoreHealth")),
                ("Hardware Info", lambda: self.executar_cmd("systeminfo"))
            ],
            "IMPRESSÃO": [
                ("Reset Spooler", self.resetar_spooler),
                ("Ver Fila", lambda: self.executar_cmd("explorer shell:::{2227A280-3AEA-1069-A2DE-08002B30309D}")),
                ("Gerenciar Impressoras", lambda: self.executar_cmd("control printers"))
            ],
            "USUARIOS": [
                ("Desbloqueio", self.desbloquear_usuario),
                ("Alterar Senha", self.resetar_senha),
                ("Logoff Forçado", self.logoff_forcado),
                ("Grupo Admin", self.add_admin)
            ],
            "SERVIÇOS": [
                ("Processos Pesados", self.processos_pesados),
                ("Serviços Travados", lambda: self.executar_cmd("services.msc")),
                ("Eventos Críticos", self.eventos_criticos)
            ],
            "FERRAMENTAS": [
                ("Painel de Controle", self.abrir_painel),
                ("Gerar Relatório", self.gerar_relatorio)
            ],
            "DIAGNÓSTICO": [
                ("Saúde do Sistema", self.diagnostico_saude),
                ("Verificar Drivers", self.verificar_drivers),
                ("Gerar Relatório Full", self.gerar_relatorio)
            ]
        }

    def criar_botoes_topo(self):
        for nome in self.menus_data:
            btn = ctk.CTkButton(self.barra_superior, text=nome, width=120, height=35, fg_color="transparent",
                                hover_color=("gray80", "gray25"), text_color=("black", "white"), command=lambda n=nome: self.alternar_menu(n))
            btn.pack(side="left", padx=2, pady=5)
            btn._nome_grupo = nome

    def alternar_menu(self, grupo):
        if self.ultimo_grupo_clicado == grupo:
            self.fechar_menu()
            return
        self.fechar_menu()
        self.ultimo_grupo_clicado = grupo
        self.menu_hover = ctk.CTkFrame(self, corner_radius=8, border_width=1, fg_color=("gray90", "gray20"), border_color=("gray70", "gray30"))
        for child in self.barra_superior.winfo_children():
            if getattr(child, '_nome_grupo', None) == grupo:
                x, y = child.winfo_x(), child.winfo_y() + child.winfo_height() + 5
                child.configure(fg_color="gray30")
                break
        self.menu_hover.place(x=x, y=y)
        self.menu_hover.lift()
        for texto, comando in self.menus_data[grupo]:
            btn = ctk.CTkButton(self.menu_hover, text=texto, command=lambda c=comando: self.clicar_opcao(c),
                                fg_color="transparent", hover_color=("gray80", "gray30"), text_color=("black", "white"), anchor="w", height=30)
            btn.pack(fill="x", padx=5, pady=2)

    def clique_fora(self, event):
        if self.menu_hover:
            x, y = event.x, event.y
            m_x, m_y = self.menu_hover.winfo_x(), self.menu_hover.winfo_y()
            if not (m_x <= x <= m_x + self.menu_hover.winfo_width() and m_y <= y <= m_y + self.menu_hover.winfo_height()):
                if y > 50: self.fechar_menu()

    def fechar_menu(self):
        if self.menu_hover: self.menu_hover.destroy(); self.menu_hover = None
        self.ultimo_grupo_clicado = None
        for child in self.barra_superior.winfo_children():
            if isinstance(child, ctk.CTkButton):
                child.configure(fg_color="transparent")

    def clicar_opcao(self, comando):
        self.fechar_menu()
        comando()

    # ================= FUNÇÕES DE EXECUÇÃO =================

    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{ts}] {msg}\n"); self.log_text.see("end")

    def executar_cmd(self, cmd):
        def run():
            self.log(f"Executando: {cmd}")
            processo = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                creationflags=0x08000000 
            )
            
            # Resultado no log interno
            if processo.stdout:
                self.log(f"Resultado:\n{processo.stdout}")
            if processo.stderr:
                self.log(f"Erro:\n{processo.stderr}")

        threading.Thread(target=run, daemon=True).start()

    def atualizar_dados(self):
        self.cpu_label.configure(text=f"CPU: {psutil.cpu_percent()}%")
        self.ram_label.configure(text=f"RAM: {psutil.virtual_memory().percent}%")
        self.after(1000, self.atualizar_dados)

    def mudar_tema(self, tema):
        ctk.set_appearance_mode(tema)

    # REDE
    def verificar_conectividade(self):
        def run():
            self.log("--- Status de Rede Atual ---")
            
            #Verifica Internet (Ping)
            ping = subprocess.run("ping -n 1 8.8.8.8", shell=True, capture_output=True, creationflags=0x08000000)
            status_internet = "ONLINE" if ping.returncode == 0 else "OFFLINE"

            nome_rede = "Desconectado"
            tipo_conexao = "Nenhuma"
            wifi_info = subprocess.run(
                "netsh wlan show interfaces", 
                shell=True, capture_output=True, text=True, encoding='cp850', 
                creationflags=0x08000000
            )

            if " SSID" in wifi_info.stdout:
                tipo_conexao = "Wi-Fi"
                for linha in wifi_info.stdout.split('\n'):
                    if " SSID" in linha and "BSSID" not in linha:
                        nome_rede = linha.split(":")[1].strip()
                        break
            else:
                # Se não for Wi-Fi, verifica se há Ethernet ativa via psutil
                stats = psutil.net_if_stats()
                for interface, info in stats.items():
                    if info.isup and "loopback" not in interface.lower():
                        if "ethernet" in interface.lower() or "conexão local" in interface.lower():
                            tipo_conexao = "Cabo (Ethernet)"
                            nome_rede = "Conexão Cabeada"
                            break

            self.log(f"INTERNET: {status_internet}")
            self.log(f"MEIO: {tipo_conexao}")
            self.log(f"REDE ATUAL: {nome_rede}")
            self.log("----------------------------")

        threading.Thread(target=run, daemon=True).start()

    def listar_redes_wifi(self):
        def run():
            self.log("--- Redes Wi-Fi Salvas no Dispositivo ---")
            try:
                resultado = subprocess.run(
                    "netsh wlan show profiles", 
                    shell=True, 
                    capture_output=True, 
                    creationflags=0x08000000
                )
                saida = resultado.stdout.decode('cp850', errors='ignore')
                
                padrao = r":\s*(.*)"
                linhas = saida.split('\n')
                
                perfis_encontrados = []
                pode_capturar = False
                for linha in linhas:
                    if "---" in linha:
                        pode_capturar = True
                        continue
                    
                    if pode_capturar:
                        match = re.search(padrao, linha)
                        if match:
                            nome = match.group(1).strip()
                            if nome and "<" not in nome:
                                perfis_encontrados.append(nome)

                if perfis_encontrados:
                    for p in sorted(set(perfis_encontrados)): 
                        self.log(f" > {p}")
                    self.log(f"\nTotal: {len(set(perfis_encontrados))} redes listadas.")
                else:
                    self.log("Nenhum perfil identificado na varredura.")

            except Exception as e:
                self.log(f"Erro Crítico: {e}")
        
        threading.Thread(target=run, daemon=True).start()

    def renovar_ip(self):
        def run():
            self.log("Renovando IP..."); subprocess.run("ipconfig /release", shell=True)
            subprocess.run("ipconfig /renew", shell=True); self.log("IP renovado.")
        threading.Thread(target=run, daemon=True).start()

    def sincronizar_ntp(self):
        def run():
            self.log("Sincronizando com ntp.br...")
            subprocess.run("net stop w32time", shell=True)
            subprocess.run('w32tm /config /manualpeerlist:"a.ntp.br b.ntp.br" /syncfromflags:manual /reliable:YES /update', shell=True)
            subprocess.run("net start w32time", shell=True)
            subprocess.run("w32tm /resync", shell=True)
            self.log("Horário sincronizado.")
        threading.Thread(target=run, daemon=True).start()

    # SISTEMA
    def limpar_temp(self):
        def run():
            self.log("Limpando temporários...")
            os.system("del /q/f/s %TEMP%\\* >nul 2>&1")
            os.system("del /q/f/s C:\\Windows\\Temp\\* >nul 2>&1")
            self.log("Limpeza concluída.")
        threading.Thread(target=run, daemon=True).start()

    def limpeza_completa(self):
        def run():
            self.log("Iniciando Limpeza de Disco (Cleanmgr)...")
            subprocess.run("cleanmgr /lowdisk /c", shell=True)
            self.log("Limpeza de disco finalizada ou janela aberta.")
        threading.Thread(target=run, daemon=True).start()

    # IMPRESSÃO
    def resetar_spooler(self):
        def run():
            self.log("Resetando Spooler...")
            # Usando creationflags para ocultar a janela de execução
            subprocess.run("net stop spooler", shell=True, creationflags=0x08000000)
            subprocess.run("net start spooler", shell=True, creationflags=0x08000000)
            self.log("Spooler OK.")
        threading.Thread(target=run, daemon=True).start()

    # USUARIOS
    def input_box(self, titulo, texto):
        dialog = ctk.CTkInputDialog(text=texto, title=titulo)
        return dialog.get_input()

    def desbloquear_usuario(self):
        u = self.input_box("Desbloquear", "Usuário:"); 
        if u: self.executar_cmd(f"net user {u} /active:yes")

    def resetar_senha(self):
        u = self.input_box("Senha", "Usuário:"); s = self.input_box("Senha", "Nova Senha:")
        if u and s: self.executar_cmd(f"net user {u} {s}")

    def logoff_forcado(self):
        u = self.input_box("Logoff", "ID da Sessão (ou nome):")
        if u: self.executar_cmd(f"logoff {u}")

    def add_admin(self):
        u = self.input_box("Admin", "Usuário:"); 
        if u: self.executar_cmd(f"net localgroup administrators {u} /add")

    # SERVIÇOS
    def processos_pesados(self):
        procs = sorted(psutil.process_iter(['name', 'cpu_percent']), key=lambda x: x.info['cpu_percent'], reverse=True)[:5]
        self.log("Top 5 CPU:")
        for p in procs: self.log(f"{p.info['name']} - {p.info['cpu_percent']}%")

    def eventos_criticos(self):
        self.log("Abrindo Event Viewer (Erros Críticos)...")
        # Abre o visualizador de eventos já filtrando erros
        self.executar_cmd('eventvwr.msc')

    # FERRAMENTAS
    def abrir_painel(self):
        self.log("Abrindo Painel de Controle...")
        self.executar_cmd("control")

    def gerar_relatorio(self):
        def run():
            n = f"Relatorio_Suporte_{datetime.now().strftime('%d%m%Y_%H%M')}.txt"
            self.log(f"Gerando {n}...")
            with open(n, "w") as f:
                f.write(f"SUPORTE TI - {datetime.now()}\n\n")
                subprocess.run("systeminfo", shell=True, stdout=f)
            self.log("Relatório salvo.")
        threading.Thread(target=run, daemon=True).start()

    #DIAGNÓSTICO
    def diagnostico_saude(self):
        def run():
            self.log("Iniciando Diagnóstico de Saúde...")
            score = 100
            alertas = []

            # 1. Teste de Internet
            t1 = subprocess.run("ping -n 1 8.8.8.8", shell=True, capture_output=True, creationflags=0x08000000)
            if t1.returncode != 0:
                score -= 40
                alertas.append("Sem acesso à Internet.")
            
            # 2. Teste de Resolução DNS
            t2 = subprocess.run("nslookup google.com", shell=True, capture_output=True, text=True, creationflags=0x08000000)
            if t2.stdout and "Address" not in t2.stdout:
                score -= 30
                alertas.append("Falha DNS")

            # 3. Uso de Recursos Críticos
            if psutil.cpu_percent() > 90:
                score -= 15
                alertas.append("Uso de CPU extremamente alto.")
            if psutil.virtual_memory().percent > 90:
                score -= 15
                alertas.append("Memória RAM quase esgotada.")

            self.log(f"--- RESULTADO: {score}/100 ---")
            if alertas:
                for a in alertas: self.log(f"[!] {a}")
            else:
                self.log("[OK] Sistema operando dentro dos parâmetros normais.")
        
        threading.Thread(target=run, daemon=True).start()

    def verificar_drivers(self):
        """Verifica dispositivos com erro usando PowerShell (Substituto do WMIC)."""
        def run():
            self.log("Verificando integridade dos drivers via PowerShell...")
            
            # Comando filtra dispositivos com status diferente de "OK"
            ps_cmd = "Get-PnpDevice | Where-Object { $_.Status -ne 'OK' } | Select-Object FriendlyName, InstanceId, Status | Format-Table"
            cmd = f'powershell -ExecutionPolicy Bypass -Command "{ps_cmd}"'
            
            processo = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                creationflags=0x08000000
            )
            
            # Verifica se houve saída (se o PS retornou algo além de espaços)
            saida = processo.stdout.strip()
            
            if saida and "FriendlyName" in saida:
                self.log("Atenção! Dispositivos com problemas encontrados:")
                self.log(saida)
            else:
                self.log("[OK] Todos os drivers estão operando normalmente.")

        threading.Thread(target=run, daemon=True).start()

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

if __name__ == "__main__":
    if is_admin():
        app = SuporteTecnicoGUI(); app.mainloop()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)