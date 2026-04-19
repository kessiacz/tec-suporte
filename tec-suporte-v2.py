import customtkinter as ctk
import psutil
import subprocess
import threading
import sys
import ctypes
import re
import base64
import time
from datetime import datetime

# CONFIGURAÇÃO DE APARÊNCIA
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

CREATE_NO_WINDOW = 0x08000000

class SuporteTecnicoGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SISTEMA DE SUPORTE")
        largura_janela = 1100
        altura_janela = 500

        self.executando_servico = False

        self.centralizar_janela(largura_janela, altura_janela)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.menu_hover = None
        self.ultimo_grupo_clicado = None
        self.ultimo_log_foi_separador = False

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
        self.log_text = ctk.CTkTextbox(self.log_frame, font=("Consolas", 12), text_color=("black", "white"), fg_color=("white", "gray15"), state="disabled")
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
            "DIAGNÓSTICO": [
                ("Saúde do Sistema", self.diagnostico_saude),
                ("Verificar Drivers", self.verificar_drivers),
            ],
            "FERRAMENTAS": [
                ("Painel de Controle", self.abrir_painel),
                ("Gerar Relatório", self.gerar_relatorio)
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

        # Frame do menu
        self.menu_hover = ctk.CTkFrame(
            self,
            corner_radius=8,
            border_width=1,
            fg_color=("gray90", "gray20"),
            border_color=("gray70", "gray30")
        )

        btn_ref = None
        for child in self.barra_superior.winfo_children():
            if getattr(child, "_nome_grupo", None) == grupo:
                btn_ref = child
                child.configure(fg_color=("gray70", "gray30"))
                break

        if not btn_ref: return
        self.update_idletasks()
        x = btn_ref.winfo_rootx() - self.winfo_rootx()
        y = btn_ref.winfo_rooty() - self.winfo_rooty() + btn_ref.winfo_height()

        # Opções
        for texto, comando in self.menus_data[grupo]:
            btn = ctk.CTkButton(
                self.menu_hover,
                text=texto,
                command=lambda cmd=comando: self.clicar_opcao(cmd),
                fg_color="transparent",
                anchor="w",
                height=30
            )
            btn.pack(fill="x", padx=5, pady=2)

        self.after(100, lambda: self._mostrar_menu(x, y))

    def _mostrar_menu(self, x, y):
        if self.menu_hover:
            self.menu_hover.place(x=x, y=y)
            self.menu_hover.lift()

    def clique_fora(self, event):
        if self.menu_hover:
            y_clique = event.y_root - self.winfo_rooty()
            if y_clique <= self.barra_superior.winfo_height():
                return
            
            m_x = self.menu_hover.winfo_x()
            m_y = self.menu_hover.winfo_y()
            m_w = self.menu_hover.winfo_width()
            m_h = self.menu_hover.winfo_height()

            x_clique = event.x_root - self.winfo_rootx()

            if not (m_x <= x_clique <= m_x + m_w and m_y <= y_clique <= m_y + m_h):
                self.fechar_menu()

    def fechar_menu(self):
        if self.menu_hover:
            self.menu_hover.destroy()
            self.menu_hover = None
        
        self.ultimo_grupo_clicado = None
        
        for child in self.barra_superior.winfo_children():
            if isinstance(child, ctk.CTkButton):
                child.configure(fg_color="transparent")

    def clicar_opcao(self, comando):
        print(f"Chamando função: {comando}")
        self.fechar_menu()
        comando()

    # ================= FUNÇÕES DE EXECUÇÃO =================

    def log(self, msg, nivel="INFO"):
        ts = datetime.now().strftime("%H:%M:%S")
        linha = f"[{ts}] [{nivel}] {msg}\n"

        def _write():
            self.log_text.configure(state="normal")
            start_index = self.log_text.index("end-1c")
            self.log_text.insert("end", linha)
            end_index = self.log_text.index("end-1c")

            tag = None
            cor = None

            if nivel == "ERRO":
                tag, cor = "erro", "red"
            elif nivel == "OK":
                tag, cor = "ok", "green"
            elif nivel == "WARN":
                tag, cor = "warn", "orange"

            # aplica cor apenas na linha correta
            if tag:
                self.log_text.tag_add(tag, start_index, end_index)
                self.log_text.tag_config(tag, foreground=cor)

            self.log_text.configure(state="disabled")
            self.log_text.see("end")

        self.after(0, _write)

    def run_thread(self, func):
        if self.executando_servico:
            self.log("Aguarde o serviço atual finalizar!", nivel="WARN")
            return

        def wrapper():
            self.executando_servico = True
            try:
                func()
            except Exception as e:
                self.log(f"Erro na thread: {e}", nivel="ERRO")
            finally:
                self.executando_servico = False
        
        threading.Thread(target=wrapper, daemon=True).start()

    def executar_cmd(self, cmd):
        def run():
            self.log(f"Executando: {cmd}")
            processo = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                creationflags=CREATE_NO_WINDOW
            )
            
            # Resultado no log interno
            if processo.stdout:
                self.log(f"Resultado:\n{processo.stdout}")
            if processo.stderr:
                self.log(f"Erro:\n{processo.stderr}")

        self.run_thread(run)

    def atualizar_dados(self):
        self.cpu_label.configure(text=f"CPU: {psutil.cpu_percent(interval=None)}%")
        self.ram_label.configure(text=f"RAM: {psutil.virtual_memory().percent}%")
        self.after(1000, self.atualizar_dados)

    def mudar_tema(self, tema):
        ctk.set_appearance_mode(tema)

    # REDE
    def verificar_conectividade(self):
        def run():
            self.log("--- Status de Rede Atual ---")
            
            #Verifica Internet (Ping)
            ping = subprocess.run("ping -n 1 8.8.8.8", shell=True, capture_output=True, creationflags=CREATE_NO_WINDOW)
            status_internet = "ONLINE" if ping.returncode == 0 else "OFFLINE"

            nome_rede = "Desconectado"
            tipo_conexao = "Nenhuma"
            wifi_info = subprocess.run(
                "netsh wlan show interfaces", 
                shell=True, capture_output=True, text=True, encoding='cp850', 
                creationflags=CREATE_NO_WINDOW
            )

            if " SSID" in wifi_info.stdout:
                tipo_conexao = "Wi-Fi"
                for linha in wifi_info.stdout.split('\n'):
                    if " SSID" in linha and "BSSID" not in linha:
                        nome_rede = linha.split(":")[1].strip()
                        break
            else:
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

        self.run_thread(run)

    def listar_redes_wifi(self):
        def run():
            self.log("--- Redes Wi-Fi no Dispositivo ---")
            try:
                interface_info = subprocess.run(
                    "netsh wlan show interfaces", 
                    shell=True, capture_output=True, text=True, encoding='cp850', 
                    creationflags=CREATE_NO_WINDOW
                ).stdout
                
                ssid_atual = ""
                for linha in interface_info.split('\n'):
                    if " SSID" in linha and "BSSID" not in linha:
                        ssid_atual = linha.split(":")[1].strip()
                        break

                resultado = subprocess.run(
                    "netsh wlan show profiles", 
                    shell=True, capture_output=True, text=True, encoding='cp850',
                    creationflags=CREATE_NO_WINDOW
                ).stdout
                
                perfis = re.findall(r"(?:Perfil de Todos os Usuários|All User Profile)\s*:\s*(.*)", resultado)
                
                if not perfis:
                    perfis = re.findall(r":\s(.*)", resultado)
                    if perfis: perfis.pop(0)

                if perfis:
                    for p in perfis:
                        p = p.strip()
                        if p == ssid_atual:
                            self.log(f" > {p} [CONECTADO]", nivel="OK")
                        else:
                            self.log(f" > {p}")
                    self.log(f"\nTotal: {len(perfis)} redes mapeadas.")
                else:
                    self.log("Nenhum perfil de rede encontrado.", nivel="WARN")

            except Exception as e:
                self.log(f"Erro ao listar redes: {e}", nivel="ERRO")
        
        self.run_thread(run)

    def renovar_ip(self):
        def run():
            self.log("Renovando IP...")
            subprocess.run("ipconfig /release", shell=True, creationflags=CREATE_NO_WINDOW)
            subprocess.run("ipconfig /renew", shell=True, creationflags=CREATE_NO_WINDOW)
            
            self.log("IP renovado.")
        
        self.run_thread(run)

    def sincronizar_ntp(self):
        def run():
            self.log("Sincronizando com ntp.br...")
            subprocess.run("net stop w32time", shell=True, creationflags=CREATE_NO_WINDOW)
            subprocess.run('w32tm /config /manualpeerlist:"a.ntp.br b.ntp.br" /syncfromflags:manual /reliable:YES /update', shell=True, creationflags=CREATE_NO_WINDOW)
            subprocess.run("net start w32time", shell=True, creationflags=CREATE_NO_WINDOW)
            subprocess.run("w32tm /resync", shell=True, creationflags=CREATE_NO_WINDOW)
            self.log("Horário sincronizado.")

        self.run_thread(run)

    # SISTEMA
    def limpar_temp(self):
        def run():
            self.log("Limpando temporários...")
            subprocess.run("del /q/f/s %TEMP%\\*", shell=True, creationflags=CREATE_NO_WINDOW)
            subprocess.run("del /q/f/s C:\\Windows\\Temp\\* >nul 2>&1", shell=True, creationflags=CREATE_NO_WINDOW)
            self.log("Limpeza concluída.")
        
        self.run_thread(run)

    def limpeza_completa(self):
        def run():
            try:
                self.log("Encerrando Explorer para limpeza profunda...", nivel="WARN")
                subprocess.run("taskkill /f /im explorer.exe", shell=True, capture_output=True, creationflags=CREATE_NO_WINDOW)
                time.sleep(1)

                # Script PowerShell
                ps_script = r"""
                $ErrorActionPreference = 'SilentlyContinue'
                
                # Windows Defender (Arquivos temporários de scan)
                Remove-Item "C:\ProgramData\Microsoft\Windows Defender\Scans\History\Store\*" -Recurse -Force
                
                # DirectX Shader Cache (Melhora performance em jogos/GUI)
                $dxPath = "$env:LOCALAPPDATA\D3DSCache"
                if (Test-Path $dxPath) { Remove-Item "$dxPath\*" -Recurse -Force }

                # Relatórios de Erros do Windows (WER)
                Remove-Item "$env:ALLUSERSPROFILE\Microsoft\Windows\WER\*" -Recurse -Force
                Remove-Item "$env:LOCALAPPDATA\Microsoft\Windows\WER\*" -Recurse -Force

                # Arquivos de Otimização de Entrega
                Remove-Item "C:\Windows\SoftwareDistribution\Download\*" -Recurse -Force

                # Caches de Miniaturas e Ícones
                Get-ChildItem "$env:LOCALAPPDATA\Microsoft\Windows\Explorer" -Filter "*.db" | Remove-Item -Force
                
                # Lixeira e Temporários Padrão
                Clear-RecycleBin -Force
                Remove-Item "$env:TEMP\*" -Recurse -Force
                Remove-Item "C:\Windows\Temp\*" -Recurse -Force
                """
                
                ps_bytes = ps_script.encode('utf-16le')
                ps_base64 = base64.b64encode(ps_bytes).decode('utf-8')
                
                self.log("Limpando Defender, DirectX e Logs de Erro...")
                subprocess.run(f"powershell -EncodedCommand {ps_base64}", shell=True, creationflags=CREATE_NO_WINDOW)

                # Volta o explorer
                subprocess.run("start explorer.exe", shell=True, creationflags=CREATE_NO_WINDOW)
                self.log("Interface restaurada. Finalizando otimização DISM...", nivel="OK")

                # Otimização de Componentes
                subprocess.run("Dism.exe /Online /Cleanup-Image /StartComponentCleanup", shell=True, creationflags=CREATE_NO_WINDOW)

                self.log("Limpeza TOTAL concluída!", nivel="OK")

            except Exception as e:
                self.log(f"Erro: {str(e)}", nivel="ERRO")
                subprocess.run("start explorer.exe", shell=True, creationflags=CREATE_NO_WINDOW)
            finally:
                self.log("--- PROCESSO FINALIZADO ---")

        self.run_thread(run)

    # IMPRESSÃO
    def resetar_spooler(self):
        def run():
            self.log("Resetando Spooler...")
            subprocess.run("net stop spooler", shell=True, creationflags=CREATE_NO_WINDOW)
            subprocess.run("net start spooler", shell=True, creationflags=CREATE_NO_WINDOW)
            self.log("Spooler OK.")

        self.run_thread(run)

    # USUARIOS
    def input_box(self, titulo, texto):
        dialog = ctk.CTkInputDialog(text=texto, title=titulo)
        return dialog.get_input()

    def desbloquear_usuario(self):
        u = self.input_box("Desbloquear", "Usuário:")
        if u:
            self.executar_cmd(f"net user {u} /active:yes")

    def resetar_senha(self):
        u = self.input_box("Senha", "Usuário:")
        s = self.input_box("Senha", "Nova Senha:")

        def run():
            if u and s:
                self.log(f"Alterando senha do usuário {u}...")
                subprocess.run(f'net user {u} "{s}"', shell=True, creationflags=CREATE_NO_WINDOW)
                self.log("Senha alterada.")

        self.run_thread(run)
            
    def logoff_forcado(self):
        u = self.input_box("Logoff", "ID da Sessão (ou nome):")
        if u: self.executar_cmd(f"logoff {u}")

    def add_admin(self):
        u = self.input_box("Admin", "Usuário:"); 
        if u: self.executar_cmd(f"net localgroup administrators {u} /add")

    # SERVIÇOS
    def processos_pesados(self):
        for p in psutil.process_iter():
            try:
                p.cpu_percent(None)
            except:
                pass

        time.sleep(1)

        procs = []
        for p in psutil.process_iter(['name']):
            try:
                procs.append((p.info['name'], p.cpu_percent(interval=0.1)))
            except:
                pass

        procs = sorted(procs, key=lambda x: x[1], reverse=True)[:5]

        self.log("Top 5 CPU:")
        for nome, cpu in procs:
            self.log(f"{nome} - {cpu}%")

    def eventos_criticos(self):
        self.log("Abrindo Event Viewer (Erros Críticos)...")
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
                subprocess.run("systeminfo", shell=True, stdout=f, creationflags=CREATE_NO_WINDOW)
            self.log("Relatório salvo.")
        
        self.run_thread(run)

    #DIAGNÓSTICO
    def diagnostico_saude(self):
        def run():
            self.log("Iniciando Diagnóstico de Saúde...")
            score = 100
            alertas = []

            # Teste de Internet
            t1 = subprocess.run("ping -n 1 8.8.8.8", shell=True, capture_output=True, creationflags=CREATE_NO_WINDOW)
            if t1.returncode != 0:
                score -= 40
                alertas.append("Sem acesso à Internet.")
            
            # Teste DNS
            t2 = subprocess.run("nslookup google.com", shell=True, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
            if t2.stdout and "Address" not in t2.stdout:
                score -= 30
                alertas.append("Falha DNS")

            # Uso de Recursos Críticos
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
        
        self.run_thread(run)

    def verificar_drivers(self):
        def run():
            self.log("Verificando integridade dos drivers via PowerShell...")
            
            # Comando filtra dispositivos com status diferente de "OK"
            ps_cmd = "Get-PnpDevice | Where-Object { $_.Status -ne 'OK' } | Select-Object FriendlyName, InstanceId, Status | Format-Table"
            cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd]
            processo = subprocess.run(cmd, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
            
            # Verifica se houve saída (se o PS retornou algo além de espaços)
            saida = processo.stdout.strip()
            
            if saida and "FriendlyName" in saida:
                self.log("Atenção! Dispositivos com problemas encontrados:")
                self.log(saida)
            else:
                self.log("[OK] Todos os drivers estão operando normalmente.")

        self.run_thread(run)

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

if __name__ == "__main__":
    if is_admin():
        app = SuporteTecnicoGUI(); app.mainloop()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)