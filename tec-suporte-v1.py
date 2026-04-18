import os
import subprocess
import threading
import time
import sys
import ctypes

# =========================
# ADMIN AUTO
# =========================
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )

if not is_admin():
    run_as_admin()
    sys.exit()

# =========================
# UTIL GERAL
# =========================
def pause():
    input("\nPressione ENTER para continuar...")

def log(msg):
    with open("log.txt", "a") as f:
        f.write(msg + "\n")

def limpar_tela():
    os.system("cls")

# =========================
# BARRA DE PROGRESSO
# =========================
def barra_progresso(stop_event, mensagem="Processando"):
    progresso = 0
    while not stop_event.is_set():
        barra = int(progresso / 2)
        sys.stdout.write(f"\r{mensagem}: [{'█'*barra}{' '*(50-barra)}] {progresso}%")
        sys.stdout.flush()
        progresso = (progresso + 1) % 101
        time.sleep(0.05)
    sys.stdout.write(f"\r{mensagem}: [{'█'*50}] 100%\n")

# =========================
# EXECUTAR
# =========================
def executar(comando, mensagem="Executando", mostrar_saida=False):
    try:
        if mostrar_saida:
            print(f"\n[{mensagem}]...\n")

            subprocess.run(f'start cmd /k "{comando}"', shell=True)

        else:
            stop_event = threading.Event()
            t = threading.Thread(target=barra_progresso, args=(stop_event, mensagem))
            t.start()

            subprocess.run(comando, shell=True,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)

            stop_event.set()
            t.join()

        log(f"OK: {comando}")

    except Exception as e:
        print(f"\n[ERRO] {e}")
        log(f"ERRO: {e}")

    pause()

# =========================
# INTERNET
# =========================
def verificar_internet():
    try:
        return subprocess.run("ping -n 1 8.8.8.8", shell=True,
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL).returncode == 0
    except:
        return False

# =========================
# FUNÇÕES
# =========================
def limpar_temp(): executar("del /q/f/s %TEMP%\\*", "Limpando temporários")
def limpar_dns(): executar("ipconfig /flushdns", "Limpando DNS")

def resetar_rede():
    executar("netsh winsock reset", "Resetando Winsock")
    executar("netsh int ip reset", "Resetando IP")
    executar("ipconfig /release", "Liberando IP")
    executar("ipconfig /renew", "Renovando IP")

def limpeza_simples():
    limpar_temp()
    limpar_dns()

def limpeza_avancada():
    executar("cleanmgr", "Limpeza de disco")

def ver_ip(): executar("ipconfig /all", "Configuração de IP", True)
def info_sistema(): executar("systeminfo", "Informações do sistema", True)

def verificar_sfc(): executar("sfc /scannow", "Verificando sistema", True)
def verificar_disco(): executar("chkdsk", "Verificando disco", True)
def reparar_windows(): executar("DISM /Online /Cleanup-Image /RestoreHealth", "Reparando Windows", True)

def ver_processos(): executar("tasklist", "Processos", True)
def usuarios_logados(): executar("whoami", "Usuário", True)

def ver_portas(): executar("netstat -ano", "Portas abertas", True)
def redes_wifi(): executar("netsh wlan show profiles", "Wi-Fi", True)

def testar_conexao():
    print("\nStatus:", "ONLINE" if verificar_internet() else "SEM INTERNET")
    pause()

# =========================
# DIAGNÓSTICO
# =========================
def diagnostico_completo():
    limpar_tela()
    print("=== DIAGNÓSTICO COMPLETO ===\n")

    score = 100
    problemas = []

    if not verificar_internet():
        score -= 30
        problemas.append("Sem internet")

    ip = subprocess.run("ipconfig", shell=True, capture_output=True, text=True)
    if "IPv4" not in ip.stdout:
        score -= 20
        problemas.append("Sem IP")

    dns = subprocess.run("nslookup google.com", shell=True, capture_output=True, text=True)
    if "Address" not in dns.stdout:
        score -= 20
        problemas.append("Falha DNS")

    print(f"\nSaúde do sistema: {score}%")

    if problemas:
        print("\nProblemas encontrados:")
        for p in problemas:
            print("-", p)

    log(f"Diagnóstico: {score}% - {problemas}")
    pause()

# =========================
# DRIVERS
# =========================
def verificar_drivers():
    limpar_tela()
    print("=== VERIFICAR DRIVERS ===\n")

    resultado = subprocess.run(
        'wmic path Win32_PnPEntity where "ConfigManagerErrorCode != 0" get Name,ConfigManagerErrorCode',
        shell=True, capture_output=True, text=True
    )

    print(resultado.stdout if resultado.stdout.strip() else "Todos os drivers OK")
    pause()

# =========================
# RELATÓRIO
# =========================
def gerar_relatorio():
    with open("relatorio.txt", "w") as f:
        subprocess.run("systeminfo", shell=True, stdout=f)
        subprocess.run("ipconfig", shell=True, stdout=f)
        subprocess.run("netstat -ano", shell=True, stdout=f)

    print("Relatório gerado!")
    pause()

# =========================
# MENU
# =========================
def main():
    while True:
        limpar_tela()
        print("""
=========================
     SUPORTE TECNICO
=========================

1 - Manutenção
2 - Sistema
3 - Rede
4 - Processos
5 - Diagnóstico
0 - Sair
""")

        op = input("Escolha: ")

        if op == "1": menu_manutencao()
        elif op == "2": menu_sistema()
        elif op == "3": menu_rede()
        elif op == "4": menu_processos()
        elif op == "5": menu_diagnostico()
        elif op == "0": break

# =========================
# SUBMENUS
# =========================
def menu_manutencao():
    while True:
        limpar_tela()
        print("""
--- MANUTENÇÃO ---
1 - Limpar temporários
2 - Limpar DNS
3 - Resetar rede
0 - Voltar
""")

        op = input("Escolha: ")

        if op == "1": limpar_temp()
        elif op == "2": limpar_dns()
        elif op == "3": resetar_rede()
        elif op == "0": break

def menu_sistema():
    while True:
        limpar_tela()
        print("""
--- SISTEMA ---
1 - Ver IP
2 - Info sistema
3 - SFC
4 - CHKDSK
5 - DISM
0 - Voltar
""")

        op = input("Escolha: ")

        if op == "1": ver_ip()
        elif op == "2": info_sistema()
        elif op == "3": verificar_sfc()
        elif op == "4": verificar_disco()
        elif op == "5": reparar_windows()
        elif op == "0": break

def menu_rede():
    while True:
        limpar_tela()
        print("""
--- REDE ---
1 - Testar conexão
2 - Portas abertas
3 - Wi-Fi
0 - Voltar
""")

        op = input("Escolha: ")

        if op == "1": testar_conexao()
        elif op == "2": ver_portas()
        elif op == "3": redes_wifi()
        elif op == "0": break

def menu_processos():
    while True:
        limpar_tela()
        print("""
--- PROCESSOS ---
1 - Ver processos
2 - Usuário atual
0 - Voltar
""")

        op = input("Escolha: ")

        if op == "1": ver_processos()
        elif op == "2": usuarios_logados()
        elif op == "0": break

def menu_diagnostico():
    while True:
        limpar_tela()
        print("""
--- DIAGNÓSTICO ---
1 - Diagnóstico completo
2 - Verificar drivers
3 - Gerar relatório
0 - Voltar
""")

        op = input("Escolha: ")

        if op == "1": diagnostico_completo()
        elif op == "2": verificar_drivers()
        elif op == "3": gerar_relatorio()
        elif op == "0": break

# =========================
# START
# =========================
main()