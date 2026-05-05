import customtkinter as ctk
import psutil
import subprocess
import threading
import sys
import ctypes
import re
import base64
import time
import queue
from datetime import datetime

# ─────────────────────────────────────────────
#  CONFIGURAÇÃO GLOBAL
# ─────────────────────────────────────────────
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")
CREATE_NO_WINDOW = 0x08000000

# Paleta de cores customizada
CORES = {
    "bg_primary":     "#0f1117",
    "bg_secondary":   "#161b26",
    "bg_tertiary":    "#1c2333",
    "sidebar_bg":     "#0d1220",
    "accent":         "#2563eb",
    "accent_hover":   "#1d4ed8",
    "accent_soft":    "#1e3a5f",
    "success":        "#22c55e",
    "warning":        "#f59e0b",
    "danger":         "#ef4444",
    "text_primary":   "#e2e8f0",
    "text_secondary": "#94a3b8",
    "text_muted":     "#4b5563",
    "border":         "#1e293b",
    "separator":      "#1e293b",
}




# ─────────────────────────────────────────────
#  UTILITÁRIOS
# ─────────────────────────────────────────────
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def hostname():
    import socket
    return socket.gethostname()


# ─────────────────────────────────────────────
#  WIDGET: BARRA LATERAL (SIDEBAR)
# ─────────────────────────────────────────────
class SidebarButton(ctk.CTkFrame):
    """Botão estilo sidebar com ícone + texto + destaque ativo."""

    def __init__(self, parent, icon, label, command, **kwargs):
        super().__init__(parent, fg_color="transparent", corner_radius=8, **kwargs)
        self._active = False
        self._command = command
        self._default_bg = "transparent"
        self._active_bg = CORES["accent_soft"]

        self.configure(cursor="hand2")

        self._icon_lbl = ctk.CTkLabel(
            self, text=icon, font=ctk.CTkFont(size=16),
            text_color=CORES["text_secondary"], width=30, anchor="center"
        )
        self._icon_lbl.grid(row=0, column=0, padx=(10, 4), pady=8)

        self._text_lbl = ctk.CTkLabel(
            self, text=label, font=self.FONTES["corpo"],
            text_color=CORES["text_secondary"], anchor="w"
        )
        self._text_lbl.grid(row=0, column=1, padx=(0, 10), pady=8, sticky="w")

        self.grid_columnconfigure(1, weight=1)

        for widget in (self, self._icon_lbl, self._text_lbl):
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def _on_click(self, _=None):
        if self._command:
            self._command(self)

    def _on_enter(self, _=None):
        if not self._active:
            self.configure(fg_color=CORES["bg_tertiary"])

    def _on_leave(self, _=None):
        if not self._active:
            self.configure(fg_color=self._default_bg)

    def set_active(self, state: bool):
        self._active = state
        color = CORES["accent_soft"] if state else self._default_bg
        text_color = "#93c5fd" if state else CORES["text_secondary"]
        self.configure(fg_color=color)
        self._icon_lbl.configure(text_color=text_color)
        self._text_lbl.configure(
            text_color=text_color,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold" if state else "normal")
        )


# ─────────────────────────────────────────────
#  WIDGET: CARD DE ESTATÍSTICA
# ─────────────────────────────────────────────
class StatCard(ctk.CTkFrame):
    def __init__(self, parent, icon, label, **kwargs):
        super().__init__(
            parent,
            fg_color=CORES["bg_tertiary"],
            corner_radius=12,
            border_width=1,
            border_color=CORES["border"],
            **kwargs
        )
        self._icon = icon
        self._label = label

        ctk.CTkLabel(self, text=icon, font=ctk.CTkFont(size=18)).pack(pady=(12, 0))
        self._val = ctk.CTkLabel(self, text="—", font=self.FONTES["stat"], text_color=CORES["text_primary"])
        self._val.pack()
        ctk.CTkLabel(self, text=label, font=self.FONTES["stat_label"], text_color=CORES["text_muted"]).pack(pady=(0, 12))

    def update(self, value: str, color: str = CORES["text_primary"]):
        self._val.configure(text=value, text_color=color)


# ─────────────────────────────────────────────
#  WIDGET: BADGE DE STATUS
# ─────────────────────────────────────────────
class StatusBadge(ctk.CTkLabel):
    _COLORS = {
        "online":  ("#bbf7d0", "#14532d"),
        "offline": ("#fecaca", "#7f1d1d"),
        "warn":    ("#fef3c7", "#78350f"),
        "info":    ("#dbeafe", "#1e3a5f"),
    }

    def __init__(self, parent, estado="info", **kwargs):
        super().__init__(parent, **kwargs)
        self.set(estado, kwargs.get("text", ""))

    def set(self, estado, texto):
        fg, tc = self._COLORS.get(estado, self._COLORS["info"])
        self.configure(
            text=f"  {texto}  ",
            fg_color=fg,
            text_color=tc,
            corner_radius=6,
            font=self.FONTES["badge"],
        )


# ─────────────────────────────────────────────
#  APLICAÇÃO PRINCIPAL
# ─────────────────────────────────────────────
class SuporteTecnicoApp(ctk.CTk):

    SIDEBAR_W = 215
    HEADER_H  = 56
    STATS_H   = 110

    def __init__(self):
        super().__init__()

        FONTES = {
            "titulo":    ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            "subtitulo": ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            "corpo":     ctk.CTkFont(family="Segoe UI", size=12),
            "pequena":   ctk.CTkFont(family="Segoe UI", size=11),
            "console":   ctk.CTkFont(family="Consolas", size=12),
            "badge":     ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            "stat":      ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            "stat_label":ctk.CTkFont(family="Segoe UI", size=10),
        }

        self.title("Suporte Técnico TI")
        self.configure(fg_color=CORES["bg_primary"])
        self._centralizar(1280, 740)
        self.minsize(1000, 600)

        # Estado
        self._executando       = False
        self._auto_scroll      = True
        self._sidebar_buttons  = {}
        self._grupo_ativo      = None
        self._log_queue: queue.Queue = queue.Queue()

        # Construção da interface
        self._build_layout()
        self._build_sidebar()
        self._build_header()
        self._build_stats_bar()
        self._build_log_area()
        self._build_status_bar()

        # Inicialização
        self._processar_log_queue()
        self._atualizar_stats()
        self._log_boas_vindas()

    # ── Layout principal ──────────────────────
    def _build_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar (coluna 0)
        self._sidebar = ctk.CTkFrame(
            self, width=self.SIDEBAR_W,
            fg_color=CORES["sidebar_bg"],
            corner_radius=0
        )
        self._sidebar.grid(row=0, column=0, sticky="nsew")
        self._sidebar.grid_propagate(False)
        self._sidebar.grid_rowconfigure(99, weight=1)  # espaçador final

        # Área principal (coluna 1)
        self._main = ctk.CTkFrame(self, fg_color=CORES["bg_primary"], corner_radius=0)
        self._main.grid(row=0, column=1, sticky="nsew")
        self._main.grid_rowconfigure(2, weight=1)
        self._main.grid_columnconfigure(0, weight=1)

    # ── Sidebar ───────────────────────────────
    def _build_sidebar(self):
        # Logo / marca
        logo_frame = ctk.CTkFrame(self._sidebar, fg_color="transparent", height=self.HEADER_H)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)

        ctk.CTkLabel(
            logo_frame,
            text="⚙  SUPORTE TI",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=CORES["accent"],
            anchor="w"
        ).place(relx=0.1, rely=0.5, anchor="w")

        # Separador
        ctk.CTkFrame(self._sidebar, height=1, fg_color=CORES["separator"]).pack(fill="x")

        # Hostname badge
        ctk.CTkLabel(
            self._sidebar,
            text=f"  🖥  {hostname()}",
            font=self.FONTES["pequena"],
            text_color=CORES["text_muted"],
            anchor="w"
        ).pack(fill="x", padx=8, pady=(10, 4))

        self._admin_badge = StatusBadge(
            self._sidebar,
            estado="online" if is_admin() else "warn",
            text="✔ Administrador" if is_admin() else "⚠ Sem Privilégios"
        )
        self._admin_badge.pack(padx=12, pady=(0, 12), anchor="w")

        ctk.CTkFrame(self._sidebar, height=1, fg_color=CORES["separator"]).pack(fill="x", pady=4)

        # Grupos do menu
        grupos = {
            "REDE":       ("🌐", self._grupo_rede),
            "SISTEMA":    ("💻", self._grupo_sistema),
            "IMPRESSÃO":  ("🖨", self._grupo_impressao),
            "USUÁRIOS":   ("👤", self._grupo_usuarios),
            "SERVIÇOS":   ("⚙",  self._grupo_servicos),
            "DIAGNÓSTICO":("🔬", self._grupo_diagnostico),
            "FERRAMENTAS":("🛠", self._grupo_ferramentas),
        }

        for nome, (icone, fn) in grupos.items():
            self._add_sidebar_section(nome)
            btn = SidebarButton(
                self._sidebar, icon=icone, label=nome,
                command=lambda b, f=fn, n=nome: self._ativar_grupo(b, f, n)
            )
            btn.pack(fill="x", padx=8, pady=2)
            self._sidebar_buttons[nome] = btn

        # Espaçador + tema
        ctk.CTkFrame(self._sidebar, fg_color="transparent").pack(expand=True, fill="both")
        ctk.CTkFrame(self._sidebar, height=1, fg_color=CORES["separator"]).pack(fill="x")

        tema_frame = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        tema_frame.pack(fill="x", padx=12, pady=10)
        ctk.CTkLabel(tema_frame, text="Tema", font=self.FONTES["pequena"],
                     text_color=CORES["text_muted"]).pack(side="left")
        ctk.CTkOptionMenu(
            tema_frame,
            values=["Dark", "Light", "System"],
            command=self._mudar_tema,
            width=100, height=28,
            font=self.FONTES["pequena"],
            fg_color=CORES["bg_tertiary"],
            button_color=CORES["accent"],
            button_hover_color=CORES["accent_hover"],
        ).pack(side="right")

    def _add_sidebar_section(self, _label):
        """Pequeno espaço antes de cada botão (sem label de seção)."""
        pass  # visual limpo – sem labels de grupo

    def _ativar_grupo(self, btn: SidebarButton, fn, nome: str):
        # Desativa anterior
        if self._grupo_ativo:
            self._sidebar_buttons[self._grupo_ativo].set_active(False)

        self._grupo_ativo = nome
        btn.set_active(True)
        fn()  # abre submenu/painel

    # ── Header ────────────────────────────────
    def _build_header(self):
        header = ctk.CTkFrame(
            self._main, height=self.HEADER_H,
            fg_color=CORES["bg_secondary"],
            corner_radius=0
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        ctk.CTkLabel(
            header, text="Painel de Suporte",
            font=self.FONTES["titulo"], text_color=CORES["text_primary"]
        ).pack(side="left", padx=20)

        # Hora / data
        self._hora_lbl = ctk.CTkLabel(
            header, text="",
            font=self.FONTES["pequena"], text_color=CORES["text_muted"]
        )
        self._hora_lbl.pack(side="right", padx=20)
        self._atualizar_hora()

    def _atualizar_hora(self):
        self._hora_lbl.configure(
            text=datetime.now().strftime("  %d/%m/%Y   %H:%M:%S  ")
        )
        self.after(1000, self._atualizar_hora)

    # ── Stats bar ─────────────────────────────
    def _build_stats_bar(self):
        bar = ctk.CTkFrame(
            self._main, height=self.STATS_H,
            fg_color=CORES["bg_secondary"],
            corner_radius=0
        )
        bar.grid(row=1, column=0, sticky="ew", padx=0)
        bar.grid_propagate(False)

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")

        self._cpu_card  = StatCard(inner, "🔄", "CPU")
        self._ram_card  = StatCard(inner, "🧠", "RAM")
        self._disk_card = StatCard(inner, "💾", "DISCO")
        self._net_card  = StatCard(inner, "🌐", "REDE")

        for i, card in enumerate((self._cpu_card, self._ram_card, self._disk_card, self._net_card)):
            card.grid(row=0, column=i, padx=8, ipadx=12)

    # ── Área de log ───────────────────────────
    def _build_log_area(self):
        log_outer = ctk.CTkFrame(
            self._main,
            fg_color=CORES["bg_secondary"],
            corner_radius=12
        )
        log_outer.grid(row=2, column=0, sticky="nsew", padx=16, pady=(12, 4))
        log_outer.grid_rowconfigure(1, weight=1)
        log_outer.grid_columnconfigure(0, weight=1)

        # Toolbar do log
        toolbar = ctk.CTkFrame(log_outer, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 0))

        ctk.CTkLabel(
            toolbar, text="📋  Log de Execução",
            font=self.FONTES["subtitulo"], text_color=CORES["text_secondary"]
        ).pack(side="left")

        # Botões da toolbar
        for txt, cmd in (
            ("⬇ Exportar",  self._exportar_log),
            ("🗑 Limpar",   self._limpar_log),
        ):
            ctk.CTkButton(
                toolbar, text=txt, command=cmd,
                width=90, height=26, font=self.FONTES["pequena"],
                fg_color=CORES["bg_tertiary"],
                hover_color=CORES["border"],
                text_color=CORES["text_secondary"],
                border_width=1, border_color=CORES["border"],
                corner_radius=6
            ).pack(side="right", padx=4)

        # Auto-scroll toggle
        self._scroll_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(
            toolbar, text="Auto-scroll",
            variable=self._scroll_var,
            font=self.FONTES["pequena"],
            text_color=CORES["text_muted"],
            button_color=CORES["accent"],
            progress_color=CORES["accent_soft"],
            onvalue=True, offvalue=False,
            width=44, height=20,
            command=lambda: setattr(self, "_auto_scroll", self._scroll_var.get())
        ).pack(side="right", padx=8)

        # Caixa de texto
        self._log_text = ctk.CTkTextbox(
            log_outer,
            font=self.FONTES["console"],
            fg_color=CORES["bg_primary"],
            text_color=CORES["text_primary"],
            corner_radius=8,
            state="disabled",
            wrap="word",
        )
        self._log_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Tags de cor
        self._log_text.tag_config("ts",   foreground=CORES["text_muted"])
        self._log_text.tag_config("ok",   foreground=CORES["success"])
        self._log_text.tag_config("erro", foreground=CORES["danger"])
        self._log_text.tag_config("warn", foreground=CORES["warning"])
        self._log_text.tag_config("info", foreground="#93c5fd")
        self._log_text.tag_config("sep",  foreground=CORES["text_muted"])
        self._log_text.tag_config("cmd",  foreground="#c084fc")

    # ── Status bar ────────────────────────────
    def _build_status_bar(self):
        bar = ctk.CTkFrame(
            self._main, height=30,
            fg_color=CORES["bg_secondary"],
            corner_radius=0
        )
        bar.grid(row=3, column=0, sticky="ew")
        bar.grid_propagate(False)

        self._status_lbl = ctk.CTkLabel(
            bar, text="  ✔  Pronto",
            font=self.FONTES["pequena"],
            text_color=CORES["success"],
            anchor="w"
        )
        self._status_lbl.pack(side="left", padx=10)

        self._progress = ctk.CTkProgressBar(
            bar, width=180, height=6,
            progress_color=CORES["accent"],
            fg_color=CORES["bg_tertiary"],
            corner_radius=3
        )
        self._progress.pack(side="right", padx=16, pady=8)
        self._progress.set(0)

    # ─────────────────────────────────────────────
    #  LOG ENGINE
    # ─────────────────────────────────────────────
    def log(self, msg: str, nivel: str = "INFO"):
        self._log_queue.put((msg, nivel))

    def _processar_log_queue(self):
        try:
            while True:
                msg, nivel = self._log_queue.get_nowait()
                self._escrever_log(msg, nivel)
        except queue.Empty:
            pass
        self.after(50, self._processar_log_queue)

    def _escrever_log(self, msg: str, nivel: str):
        ts = datetime.now().strftime("%H:%M:%S")

        niveis = {
            "OK":   ("✔", "ok"),
            "ERRO": ("✖", "erro"),
            "WARN": ("⚠", "warn"),
            "CMD":  ("›", "cmd"),
            "SEP":  ("", "sep"),
        }
        icone, tag = niveis.get(nivel, ("·", "info"))

        self._log_text.configure(state="normal")

        if nivel == "SEP":
            linha = f"{'─' * 60}\n"
            start = self._log_text.index("end-1c")
            self._log_text.insert("end", linha)
            end = self._log_text.index("end-1c")
            self._log_text.tag_add("sep", start, end)
        else:
            # Timestamp
            ts_start = self._log_text.index("end-1c")
            self._log_text.insert("end", f"[{ts}] ")
            ts_end = self._log_text.index("end-1c")
            self._log_text.tag_add("ts", ts_start, ts_end)

            # Ícone + nível
            nivel_start = ts_end
            self._log_text.insert("end", f"{icone} ")
            nivel_end = self._log_text.index("end-1c")
            self._log_text.tag_add(tag, nivel_start, nivel_end)

            # Mensagem
            msg_start = nivel_end
            self._log_text.insert("end", f"{msg}\n")
            msg_end = self._log_text.index("end-1c")
            if nivel not in ("INFO",):
                self._log_text.tag_add(tag, msg_start, msg_end)

        self._log_text.configure(state="disabled")

        if self._auto_scroll:
            self._log_text.see("end")

    def _log_boas_vindas(self):
        self.log("SEP", "SEP")
        self.log(f"SISTEMA DE SUPORTE TI  |  {hostname()}  |  {datetime.now().strftime('%d/%m/%Y')}", "INFO")
        self.log(f"Modo Admin: {'✔ Ativo' if is_admin() else '✖ Inativo — algumas funções podem falhar'}", 
                 "OK" if is_admin() else "WARN")
        self.log("SEP", "SEP")

    # ─────────────────────────────────────────────
    #  THREADING
    # ─────────────────────────────────────────────
    def _run(self, func, nome_op: str = "Operação"):
        if self._executando:
            self.log("Aguarde a operação atual finalizar.", "WARN")
            return

        def wrapper():
            self._executando = True
            self._set_status(f"⏳  {nome_op}...", CORES["warning"])
            self._progress.configure(mode="indeterminate")
            self._progress.start()
            try:
                func()
            except Exception as e:
                self.log(f"Erro inesperado: {e}", "ERRO")
            finally:
                self._executando = False
                self._progress.stop()
                self._progress.configure(mode="determinate")
                self._progress.set(0)
                self._set_status("✔  Pronto", CORES["success"])

        threading.Thread(target=wrapper, daemon=True).start()

    def _set_status(self, texto: str, cor: str = CORES["text_primary"]):
        self.after(0, lambda: self._status_lbl.configure(text=f"  {texto}", text_color=cor))

    def _cmd(self, cmd: str, nome: str = None):
        """Executa comando de shell e loga resultado."""
        def run():
            self.log(f"$ {cmd}", "CMD")
            res = subprocess.run(
                cmd, shell=True,
                capture_output=True, text=True,
                encoding="utf-8", errors="ignore",
                creationflags=CREATE_NO_WINDOW
            )
            if res.stdout.strip():
                self.log(res.stdout.strip())
            if res.stderr.strip():
                self.log(res.stderr.strip(), "ERRO")

        self._run(run, nome or cmd[:40])

    def _ps(self, script: str, nome: str = "PowerShell"):
        """Executa script PowerShell codificado em base64."""
        def run():
            self.log(f"[PS] {nome}", "CMD")
            ps_b64 = base64.b64encode(script.encode("utf-16le")).decode()
            res = subprocess.run(
                f"powershell -NoProfile -ExecutionPolicy Bypass -EncodedCommand {ps_b64}",
                shell=True, capture_output=True, text=True,
                creationflags=CREATE_NO_WINDOW
            )
            if res.stdout.strip():
                self.log(res.stdout.strip())
            if res.stderr.strip():
                self.log(res.stderr.strip(), "ERRO")

        self._run(run, nome)

    # ─────────────────────────────────────────────
    #  STATS
    # ─────────────────────────────────────────────
    def _atualizar_stats(self):
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent

        def _cor(val):
            if val >= 90: return CORES["danger"]
            if val >= 70: return CORES["warning"]
            return CORES["success"]

        self._cpu_card.update(f"{cpu:.0f}%", _cor(cpu))
        self._ram_card.update(f"{ram:.0f}%", _cor(ram))
        self._disk_card.update(f"{disk:.0f}%", _cor(disk))

        # Velocidade de rede aproximada
        try:
            net = psutil.net_io_counters()
            if hasattr(self, "_net_prev"):
                dt = 1
                sent_kb = (net.bytes_sent - self._net_prev.bytes_sent) / 1024 / dt
                recv_kb = (net.bytes_recv - self._net_prev.bytes_recv) / 1024 / dt
                self._net_card.update(f"↑{sent_kb:.0f} ↓{recv_kb:.0f}", CORES["text_primary"])
            else:
                self._net_card.update("Medindo…", CORES["text_muted"])
            self._net_prev = net
        except:
            self._net_card.update("N/D", CORES["text_muted"])

        self.after(1000, self._atualizar_stats)

    # ─────────────────────────────────────────────
    #  PAINÉIS DE AÇÕES (inline popup)
    # ─────────────────────────────────────────────
    def _fechar_painel(self):
        if hasattr(self, "_painel") and self._painel:
            self._painel.destroy()
            self._painel = None

    def _abrir_painel(self, titulo: str, itens: list):
        """Abre um painel flutuante com botões de ação."""
        self._fechar_painel()

        self._painel = ctk.CTkToplevel(self)
        self._painel.title(titulo)
        self._painel.configure(fg_color=CORES["bg_secondary"])
        self._painel.resizable(False, False)
        self._painel.attributes("-topmost", True)
        self._painel.grab_set()

        w, h = 280, 60 + 48 * len(itens)
        px = self.winfo_x() + self.SIDEBAR_W + 20
        py = self.winfo_y() + self.HEADER_H + self.STATS_H + 20
        self._painel.geometry(f"{w}x{h}+{px}+{py}")

        ctk.CTkLabel(
            self._painel, text=titulo,
            font=self.FONTES["subtitulo"],
            text_color=CORES["text_secondary"]
        ).pack(pady=(14, 6), padx=16, anchor="w")

        ctk.CTkFrame(self._painel, height=1, fg_color=CORES["separator"]).pack(fill="x")

        for label, cmd in itens:
            def _make_cmd(c):
                def _():
                    self._fechar_painel()
                    c()
                return _

            ctk.CTkButton(
                self._painel, text=label,
                command=_make_cmd(cmd),
                height=36, anchor="w",
                fg_color="transparent",
                hover_color=CORES["bg_tertiary"],
                text_color=CORES["text_primary"],
                font=self.FONTES["corpo"],
                corner_radius=6,
            ).pack(fill="x", padx=8, pady=3)

        self._painel.bind("<Escape>", lambda _: self._fechar_painel())
        self._painel.protocol("WM_DELETE_WINDOW", self._fechar_painel)

    # ─────────────────────────────────────────────
    #  GRUPOS DE AÇÕES
    # ─────────────────────────────────────────────
    def _grupo_rede(self):
        self.log("SEP", "SEP")
        self.log("MÓDULO: REDE", "INFO")
        self._abrir_painel("🌐  Rede", [
            ("Status de Conexão",    self._rede_status),
            ("Redes Wi-Fi Salvas",   self._rede_wifi_salvas),
            ("IP / MAC / DNS",       lambda: self._cmd("ipconfig /all", "IP/MAC/DNS")),
            ("Flush DNS",            lambda: self._cmd("ipconfig /flushdns", "Flush DNS")),
            ("Renovar IP",           self._rede_renovar_ip),
            ("Sincronizar NTP",      self._rede_ntp),
            ("Traceroute 8.8.8.8",   lambda: self._cmd("tracert 8.8.8.8", "Traceroute")),
            ("Diagnóstico de Rede",  self._rede_diagnostico),
        ])

    def _grupo_sistema(self):
        self.log("SEP", "SEP")
        self.log("MÓDULO: SISTEMA", "INFO")
        self._abrir_painel("💻  Sistema", [
            ("Limpar Temporários",   self._sis_limpar_temp),
            ("Limpeza Avançada",     self._sis_limpeza_completa),
            ("SFC Scan",             lambda: self._cmd("sfc /scannow", "SFC Scan")),
            ("DISM RestoreHealth",   lambda: self._cmd("DISM /Online /Cleanup-Image /RestoreHealth", "DISM")),
            ("Informações Hardware", lambda: self._cmd("systeminfo", "Hardware Info")),
            ("Política de Grupo",    lambda: self._cmd("gpupdate /force", "GPUpdate")),
        ])

    def _grupo_impressao(self):
        self.log("SEP", "SEP")
        self.log("MÓDULO: IMPRESSÃO", "INFO")
        self._abrir_painel("🖨  Impressão", [
            ("Reset Spooler",         self._imp_resetar_spooler),
            ("Ver Fila de Impressão", lambda: self._cmd("explorer shell:::{2227A280-3AEA-1069-A2DE-08002B30309D}", "Fila")),
            ("Gerenciar Impressoras", lambda: self._cmd("control printers", "Impressoras")),
            ("Reinstalar Driver",     self._imp_reinstalar_driver),
        ])

    def _grupo_usuarios(self):
        self.log("SEP", "SEP")
        self.log("MÓDULO: USUÁRIOS", "INFO")
        self._abrir_painel("👤  Usuários", [
            ("Desbloquear Conta",  self._usr_desbloquear),
            ("Alterar Senha",      self._usr_senha),
            ("Logoff Forçado",     self._usr_logoff),
            ("Adicionar ao Admin", self._usr_add_admin),
            ("Listar Usuários",    lambda: self._cmd("net user", "Listar Usuários")),
        ])

    def _grupo_servicos(self):
        self.log("SEP", "SEP")
        self.log("MÓDULO: SERVIÇOS", "INFO")
        self._abrir_painel("⚙  Serviços", [
            ("Top 5 Processos CPU",  self._svc_processos_pesados),
            ("Top 5 Processos RAM",  self._svc_processos_ram),
            ("Gerenciador de Serv.", lambda: self._cmd("services.msc", "Serviços")),
            ("Event Viewer",        lambda: self._cmd("eventvwr.msc", "Event Viewer")),
            ("Eventos Críticos",    self._svc_eventos_criticos),
        ])

    def _grupo_diagnostico(self):
        self.log("SEP", "SEP")
        self.log("MÓDULO: DIAGNÓSTICO", "INFO")
        self._abrir_painel("🔬  Diagnóstico", [
            ("Saúde do Sistema",     self._diag_saude),
            ("Verificar Drivers",   self._diag_drivers),
            ("Teste de Memória",    lambda: self._cmd("mdsched", "Memória")),
            ("SMART de Disco",      self._diag_smart),
            ("Tempo de Boot",       self._diag_boot_time),
        ])

    def _grupo_ferramentas(self):
        self.log("SEP", "SEP")
        self.log("MÓDULO: FERRAMENTAS", "INFO")
        self._abrir_painel("🛠  Ferramentas", [
            ("Painel de Controle",  lambda: self._cmd("control", "Painel")),
            ("Gerenc. de Tarefas",  lambda: self._cmd("taskmgr", "TaskMgr")),
            ("Editor do Registro",  lambda: self._cmd("regedit", "Regedit")),
            ("Gerar Relatório",     self._fer_relatorio),
            ("Abrir Log Externo",   self._fer_abrir_log),
        ])

    # ─────────────────────────────────────────────
    #  IMPLEMENTAÇÕES — REDE
    # ─────────────────────────────────────────────
    def _rede_status(self):
        def run():
            self.log("Verificando conectividade...")
            ping = subprocess.run("ping -n 1 8.8.8.8", shell=True,
                                  capture_output=True, creationflags=CREATE_NO_WINDOW)
            internet = ping.returncode == 0

            wifi = subprocess.run("netsh wlan show interfaces", shell=True,
                                  capture_output=True, text=True, encoding="utf-8", errors="ignore",
                                  creationflags=CREATE_NO_WINDOW)
            ssid = "—"
            tipo = "Cabo (Ethernet)"
            if " SSID" in wifi.stdout:
                tipo = "Wi-Fi"
                for l in wifi.stdout.split("\n"):
                    if " SSID" in l and "BSSID" not in l:
                        ssid = l.split(":", 1)[1].strip()
                        break

            self.log(f"Internet   : {'ONLINE' if internet else 'OFFLINE'}", "OK" if internet else "ERRO")
            self.log(f"Conexão    : {tipo}")
            self.log(f"SSID       : {ssid}")

            # Latência
            res = subprocess.run("ping -n 4 8.8.8.8", shell=True,
                                 capture_output=True, text=True, encoding="utf-8", errors="ignore",
                                 creationflags=CREATE_NO_WINDOW)
            for l in res.stdout.split("\n"):
                if "Média" in l or "Average" in l:
                    self.log(f"Latência   : {l.strip()}")
                    break

        self._run(run, "Status de Rede")

    def _rede_wifi_salvas(self):
        def run():
            self.log("Listando perfis Wi-Fi salvos...")
            iface = subprocess.run("netsh wlan show interfaces", shell=True,
                                   capture_output=True, text=True, encoding="utf-8", errors="ignore",
                                   creationflags=CREATE_NO_WINDOW).stdout
            ssid_atual = ""
            for l in iface.split("\n"):
                if " SSID" in l and "BSSID" not in l:
                    ssid_atual = l.split(":", 1)[1].strip()
                    break

            res = subprocess.run("netsh wlan show profiles", shell=True,
                                 capture_output=True, text=True, encoding="utf-8", errors="ignore",
                                 creationflags=CREATE_NO_WINDOW).stdout

            perfis = re.findall(r"(?:Perfil de Todos os Usuários|All User Profile)\s*:\s*(.*)", res)
            if not perfis:
                perfis = [x for x in re.findall(r":\s(.*)", res) if x.strip()]

            if perfis:
                for p in perfis:
                    p = p.strip()
                    nivel = "OK" if p == ssid_atual else "INFO"
                    sufixo = " [CONECTADO]" if p == ssid_atual else ""
                    self.log(f"  {p}{sufixo}", nivel)
                self.log(f"Total: {len(perfis)} redes mapeadas.")
            else:
                self.log("Nenhum perfil encontrado.", "WARN")

        self._run(run, "Wi-Fi Salvas")

    def _rede_renovar_ip(self):
        def run():
            self.log("Liberando IP atual...")
            subprocess.run("ipconfig /release", shell=True, creationflags=CREATE_NO_WINDOW)
            self.log("Solicitando novo IP (DHCP)...")
            subprocess.run("ipconfig /renew",  shell=True, creationflags=CREATE_NO_WINDOW)
            self.log("IP renovado com sucesso.", "OK")

        self._run(run, "Renovar IP")

    def _rede_ntp(self):
        def run():
            self.log("Sincronizando horário com ntp.br...")
            cmds = [
                "net stop w32time",
                'w32tm /config /manualpeerlist:"a.ntp.br b.ntp.br" /syncfromflags:manual /reliable:YES /update',
                "net start w32time",
                "w32tm /resync",
            ]
            for c in cmds:
                subprocess.run(c, shell=True, creationflags=CREATE_NO_WINDOW)
            self.log("Horário sincronizado.", "OK")

        self._run(run, "NTP Sync")

    def _rede_diagnostico(self):
        def run():
            self.log("Diagnóstico de rede completo...")
            testes = [
                ("Gateway",   "ping -n 2 192.168.1.1"),
                ("DNS 8.8.8.8","ping -n 2 8.8.8.8"),
                ("Google.com","ping -n 2 google.com"),
            ]
            for nome, cmd in testes:
                r = subprocess.run(cmd, shell=True, capture_output=True,
                                   creationflags=CREATE_NO_WINDOW)
                self.log(f"{nome:12}: {'OK' if r.returncode == 0 else 'FALHA'}",
                         "OK" if r.returncode == 0 else "ERRO")

        self._run(run, "Diagnóstico de Rede")

    # ─────────────────────────────────────────────
    #  IMPLEMENTAÇÕES — SISTEMA
    # ─────────────────────────────────────────────
    def _sis_limpar_temp(self):
        def run():
            self.log("Removendo arquivos temporários...")
            cmds = [
                "del /q /f /s %TEMP%\\*",
                "del /q /f /s C:\\Windows\\Temp\\*",
            ]
            for c in cmds:
                subprocess.run(c, shell=True, creationflags=CREATE_NO_WINDOW)
            self.log("Temporários removidos.", "OK")

        self._run(run, "Limpar Temp")

    def _sis_limpeza_completa(self):
        def run():
            self.log("Iniciando limpeza profunda do sistema...", "WARN")
            self.log("Encerrando Explorer temporariamente...")
            subprocess.run("taskkill /f /im explorer.exe", shell=True,
                           capture_output=True, creationflags=CREATE_NO_WINDOW)
            time.sleep(1)

            script = r"""
$ErrorActionPreference = 'SilentlyContinue'
Remove-Item "C:\ProgramData\Microsoft\Windows Defender\Scans\History\Store\*" -Recurse -Force
$dx = "$env:LOCALAPPDATA\D3DSCache"
if (Test-Path $dx) { Remove-Item "$dx\*" -Recurse -Force }
Remove-Item "$env:ALLUSERSPROFILE\Microsoft\Windows\WER\*" -Recurse -Force
Remove-Item "$env:LOCALAPPDATA\Microsoft\Windows\WER\*"   -Recurse -Force
Remove-Item "C:\Windows\SoftwareDistribution\Download\*"  -Recurse -Force
Get-ChildItem "$env:LOCALAPPDATA\Microsoft\Windows\Explorer" -Filter "*.db" | Remove-Item -Force
Clear-RecycleBin -Force
Remove-Item "$env:TEMP\*"         -Recurse -Force
Remove-Item "C:\Windows\Temp\*"  -Recurse -Force
"""
            self._run_ps_encoded(script)
            subprocess.run("start explorer.exe", shell=True, creationflags=CREATE_NO_WINDOW)
            self.log("Interface restaurada. Executando DISM ComponentCleanup...")
            subprocess.run("Dism.exe /Online /Cleanup-Image /StartComponentCleanup",
                           shell=True, creationflags=CREATE_NO_WINDOW)
            self.log("Limpeza profunda concluída.", "OK")

        self._run(run, "Limpeza Avançada")

    def _run_ps_encoded(self, script: str):
        b64 = base64.b64encode(script.encode("utf-16le")).decode()
        subprocess.run(f"powershell -NoProfile -ExecutionPolicy Bypass -EncodedCommand {b64}",
                       shell=True, creationflags=CREATE_NO_WINDOW)

    # ─────────────────────────────────────────────
    #  IMPLEMENTAÇÕES — IMPRESSÃO
    # ─────────────────────────────────────────────
    def _imp_resetar_spooler(self):
        def run():
            self.log("Parando serviço Spooler...")
            subprocess.run("net stop spooler", shell=True, creationflags=CREATE_NO_WINDOW)
            self.log("Limpando fila de impressão...")
            subprocess.run("del /Q /F /S %systemroot%\\System32\\spool\\PRINTERS\\*",
                           shell=True, creationflags=CREATE_NO_WINDOW)
            self.log("Reiniciando Spooler...")
            subprocess.run("net start spooler", shell=True, creationflags=CREATE_NO_WINDOW)
            self.log("Spooler reiniciado com sucesso.", "OK")

        self._run(run, "Reset Spooler")

    def _imp_reinstalar_driver(self):
        self.log("Abrindo gerenciamento de impressoras para reinstalação manual.", "WARN")
        self._cmd("control printers")

    # ─────────────────────────────────────────────
    #  IMPLEMENTAÇÕES — USUÁRIOS
    # ─────────────────────────────────────────────
    def _input(self, titulo: str, prompt: str) -> str | None:
        d = ctk.CTkInputDialog(text=prompt, title=titulo)
        return d.get_input()

    def _usr_desbloquear(self):
        u = self._input("Desbloquear Conta", "Nome do usuário:")
        if u:
            self._cmd(f"net user {u} /active:yes", f"Desbloquear {u}")

    def _usr_senha(self):
        u = self._input("Alterar Senha", "Nome do usuário:")
        s = self._input("Alterar Senha", "Nova senha:") if u else None
        if u and s:
            def run():
                self.log(f"Alterando senha de '{u}'...")
                subprocess.run(f'net user {u} "{s}"', shell=True, creationflags=CREATE_NO_WINDOW)
                self.log("Senha alterada com sucesso.", "OK")
            self._run(run, "Alterar Senha")

    def _usr_logoff(self):
        u = self._input("Logoff Forçado", "ID ou nome da sessão:")
        if u: self._cmd(f"logoff {u}", "Logoff Forçado")

    def _usr_add_admin(self):
        u = self._input("Adicionar Administrador", "Nome do usuário:")
        if u: self._cmd(f"net localgroup administrators {u} /add", "Add Admin")

    # ─────────────────────────────────────────────
    #  IMPLEMENTAÇÕES — SERVIÇOS
    # ─────────────────────────────────────────────
    def _svc_processos_pesados(self):
        def run():
            for p in psutil.process_iter():
                try: p.cpu_percent(None)
                except: pass
            time.sleep(1.2)
            procs = []
            for p in psutil.process_iter(["name", "pid"]):
                try: procs.append((p.info["name"], p.info["pid"], p.cpu_percent(interval=0.1)))
                except: pass
            top = sorted(procs, key=lambda x: x[2], reverse=True)[:5]
            self.log("Top 5 por CPU:")
            for nome, pid, cpu in top:
                self.log(f"  {nome:<30} PID:{pid:<6} CPU:{cpu:.1f}%",
                         "WARN" if cpu > 50 else "INFO")

        self._run(run, "Processos CPU")

    def _svc_processos_ram(self):
        def run():
            procs = []
            for p in psutil.process_iter(["name", "pid", "memory_info"]):
                try:
                    mb = p.info["memory_info"].rss / 1024 / 1024
                    procs.append((p.info["name"], p.info["pid"], mb))
                except: pass
            top = sorted(procs, key=lambda x: x[2], reverse=True)[:5]
            self.log("Top 5 por RAM:")
            for nome, pid, mb in top:
                self.log(f"  {nome:<30} PID:{pid:<6} RAM:{mb:.0f} MB",
                         "WARN" if mb > 500 else "INFO")

        self._run(run, "Processos RAM")

    def _svc_eventos_criticos(self):
        def run():
            self.log("Buscando eventos críticos (últimas 24h)...")
            ps = """
Get-WinEvent -FilterHashtable @{LogName='System'; Level=1,2; StartTime=(Get-Date).AddHours(-24)} -MaxEvents 10 -ErrorAction SilentlyContinue |
Select-Object TimeCreated, Id, Message | Format-Table -AutoSize
"""
            self._run_ps_encoded(ps)
            self.log("Consulta concluída.", "OK")

        self._run(run, "Eventos Críticos")

    # ─────────────────────────────────────────────
    #  IMPLEMENTAÇÕES — DIAGNÓSTICO
    # ─────────────────────────────────────────────
    def _diag_saude(self):
        def run():
            self.log("Iniciando diagnóstico completo...")
            score = 100
            alertas = []

            # Internet
            p1 = subprocess.run("ping -n 1 8.8.8.8", shell=True,
                                 capture_output=True, creationflags=CREATE_NO_WINDOW)
            if p1.returncode != 0:
                score -= 30; alertas.append("Sem acesso à internet")

            # DNS
            p2 = subprocess.run("nslookup google.com", shell=True,
                                 capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
            if "Address" not in p2.stdout:
                score -= 20; alertas.append("Falha na resolução DNS")

            # CPU
            cpu = psutil.cpu_percent(interval=1)
            if cpu > 90: score -= 15; alertas.append(f"CPU crítico: {cpu:.0f}%")

            # RAM
            ram = psutil.virtual_memory().percent
            if ram > 90: score -= 15; alertas.append(f"RAM crítica: {ram:.0f}%")

            # Disco
            disk = psutil.disk_usage("/").percent
            if disk > 90: score -= 10; alertas.append(f"Disco quase cheio: {disk:.0f}%")

            # Resultado
            nivel = "OK" if score >= 80 else ("WARN" if score >= 50 else "ERRO")
            self.log(f"RESULTADO: {score}/100", nivel)
            if alertas:
                for a in alertas: self.log(f"  ⚠ {a}", "WARN")
            else:
                self.log("  Sistema operando dentro dos parâmetros normais.", "OK")

        self._run(run, "Diagnóstico de Saúde")

    def _diag_drivers(self):
        def run():
            self.log("Verificando integridade dos drivers...")
            ps = "Get-PnpDevice | Where-Object { $_.Status -ne 'OK' } | Select-Object FriendlyName, InstanceId, Status | Format-Table -AutoSize"
            r = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
                capture_output=True, text=True, creationflags=CREATE_NO_WINDOW
            )
            saida = r.stdout.strip()
            if saida and "FriendlyName" in saida:
                self.log("Dispositivos com problemas:", "WARN")
                self.log(saida)
            else:
                self.log("Todos os drivers estão operando normalmente.", "OK")

        self._run(run, "Verificar Drivers")

    def _diag_smart(self):
        def run():
            self.log("Verificando saúde do disco (SMART via WMI)...")
            ps = """
Get-WmiObject -Namespace root\\wmi -Class MSStorageDriver_FailurePredictStatus |
Select-Object InstanceName, PredictFailure, Reason | Format-List
"""
            self._run_ps_encoded(ps)

        self._run(run, "SMART Disco")

    def _diag_boot_time(self):
        def run():
            boot = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot
            h, r = divmod(int(uptime.total_seconds()), 3600)
            m, s = divmod(r, 60)
            self.log(f"Boot em : {boot.strftime('%d/%m/%Y %H:%M:%S')}")
            self.log(f"Uptime  : {h}h {m}m {s}s")

        self._run(run, "Tempo de Boot")

    # ─────────────────────────────────────────────
    #  IMPLEMENTAÇÕES — FERRAMENTAS
    # ─────────────────────────────────────────────
    def _fer_relatorio(self):
        def run():
            nome = f"Relatorio_TI_{datetime.now().strftime('%d%m%Y_%H%M%S')}.txt"
            self.log(f"Gerando relatório: {nome}...")
            with open(nome, "w", encoding="utf-8") as f:
                f.write(f"RELATÓRIO DE SUPORTE TI\n")
                f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Host: {hostname()}\n")
                f.write("=" * 60 + "\n\n")

                res = subprocess.run("systeminfo", shell=True, capture_output=True,
                                     text=True, encoding="utf-8", errors="ignore", creationflags=CREATE_NO_WINDOW)
                f.write(res.stdout)
            self.log(f"Relatório salvo: {nome}", "OK")

        self._run(run, "Gerar Relatório")

    def _fer_abrir_log(self):
        def run():
            nome = f"log_suporte_{datetime.now().strftime('%d%m%Y_%H%M%S')}.txt"
            self.log(f"Exportando log para: {nome}")
            conteudo = self._log_text.get("1.0", "end")
            with open(nome, "w", encoding="utf-8") as f:
                f.write(conteudo)
            self.log(f"Log exportado: {nome}", "OK")
            subprocess.run(f"notepad {nome}", shell=True, creationflags=CREATE_NO_WINDOW)

        self._run(run, "Abrir Log")

    # ─────────────────────────────────────────────
    #  CONTROLES DE LOG
    # ─────────────────────────────────────────────
    def _limpar_log(self):
        self._log_text.configure(state="normal")
        self._log_text.delete("1.0", "end")
        self._log_text.configure(state="disabled")
        self._log_boas_vindas()

    def _exportar_log(self):
        self._fer_abrir_log()

    # ─────────────────────────────────────────────
    #  TEMA
    # ─────────────────────────────────────────────
    def _mudar_tema(self, tema: str):
        ctk.set_appearance_mode(tema)

    # ─────────────────────────────────────────────
    #  UTILIDADES
    # ─────────────────────────────────────────────
    def _centralizar(self, w: int, h: int):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    if is_admin():
        app = SuporteTecnicoApp()
        app.mainloop()
    else:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
