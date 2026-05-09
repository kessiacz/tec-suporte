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

TEMAS_CORES = {
    "Dark": {
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
        "hover_menu_bg":  "#1a2235",
    },
    "Light": {
        "bg_primary":     "#f1f5f9",
        "bg_secondary":   "#ffffff",
        "bg_tertiary":    "#e2e8f0",
        "sidebar_bg":     "#dde3ed",
        "accent":         "#2563eb",
        "accent_hover":   "#1d4ed8",
        "accent_soft":    "#bfdbfe",
        "success":        "#16a34a",
        "warning":        "#d97706",
        "danger":         "#dc2626",
        "text_primary":   "#0d1220",
        "text_secondary": "#334155",
        "text_muted":     "#94a3b8",
        "border":         "#cbd5e1",
        "separator":      "#cbd5e1",
        "hover_menu_bg":  "#f8fafc",
    },
    "Azul": {
        "bg_primary":     "#0a0f1e",
        "bg_secondary":   "#0d1530",
        "bg_tertiary":    "#101c3a",
        "sidebar_bg":     "#080d1a",
        "accent":         "#3b82f6",
        "accent_hover":   "#2563eb",
        "accent_soft":    "#1e3a8a",
        "success":        "#22c55e",
        "warning":        "#f59e0b",
        "danger":         "#ef4444",
        "text_primary":   "#e0f2fe",
        "text_secondary": "#93c5fd",
        "text_muted":     "#3b5070",
        "border":         "#1e3a8a",
        "separator":      "#1e3a8a",
        "hover_menu_bg":  "#0f1f45",
    },
    "Verde": {
        "bg_primary":     "#071008",
        "bg_secondary":   "#0d1a0f",
        "bg_tertiary":    "#112214",
        "sidebar_bg":     "#060e08",
        "accent":         "#22c55e",
        "accent_hover":   "#16a34a",
        "accent_soft":    "#14532d",
        "success":        "#4ade80",
        "warning":        "#f59e0b",
        "danger":         "#ef4444",
        "text_primary":   "#dcfce7",
        "text_secondary": "#86efac",
        "text_muted":     "#365c3e",
        "border":         "#14532d",
        "separator":      "#14532d",
        "hover_menu_bg":  "#0a1f0c",
    },
}

CORES = TEMAS_CORES["Dark"]


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
#  Sem border_width → sem traço preto nas bordas
# ─────────────────────────────────────────────
class SidebarButton(ctk.CTkFrame):
    """Botão sidebar com ícone + texto. Ativado por clique."""

    def __init__(self, parent, icon, label, fontes, **kwargs):
        super().__init__(
            parent,
            fg_color="transparent",
            corner_radius=6,
            border_width=0,   # ← sem borda preta
            **kwargs
        )
        self._active = False
        self.FONTES = fontes

        self.configure(cursor="hand2")

        self._icon_lbl = ctk.CTkLabel(
            self, text=icon, font=ctk.CTkFont(size=13),
            text_color=CORES["text_secondary"], width=22, anchor="center"
        )
        self._icon_lbl.grid(row=0, column=0, padx=(6, 2), pady=6)

        self._text_lbl = ctk.CTkLabel(
            self, text=label, font=fontes["pequena"],
            text_color=CORES["text_secondary"], anchor="w"
        )
        self._text_lbl.grid(row=0, column=1, padx=(0, 6), pady=6, sticky="w")

        # Indicador de seta (►) à direita
        self._arrow_lbl = ctk.CTkLabel(
            self, text="›", font=ctk.CTkFont(size=14),
            text_color=CORES["text_muted"], width=14, anchor="center"
        )
        self._arrow_lbl.grid(row=0, column=2, padx=(0, 6), pady=6)

        self.grid_columnconfigure(1, weight=1)

    def on_hover_enter(self, _=None):
        if not self._active:
            self.configure(fg_color=CORES["bg_tertiary"])
            self._arrow_lbl.configure(text_color=CORES["text_secondary"])

    def on_hover_leave(self, _=None):
        if not self._active:
            self.configure(fg_color="transparent")
            self._arrow_lbl.configure(text_color=CORES["text_muted"])

    def set_active(self, state: bool):
        self._active = state
        color      = CORES["accent_soft"] if state else "transparent"
        text_color = "#93c5fd" if state else CORES["text_secondary"]
        arrow_col  = "#93c5fd" if state else CORES["text_muted"]
        self.configure(fg_color=color)
        self._icon_lbl.configure(text_color=text_color)
        self._text_lbl.configure(
            text_color=text_color,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold" if state else "normal")
        )
        self._arrow_lbl.configure(
            text=("▾" if state else "›"),
            text_color=arrow_col
        )

    def refresh_colors(self):
        if self._active:
            self.set_active(True)
        else:
            self.configure(fg_color="transparent")
            self._icon_lbl.configure(text_color=CORES["text_secondary"])
            self._text_lbl.configure(
                text_color=CORES["text_secondary"],
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="normal")
            )
            self._arrow_lbl.configure(text="›", text_color=CORES["text_muted"])


# ─────────────────────────────────────────────
#  WIDGET: MENU DROPDOWN (CLICK)
#  Renderizado como CTkFrame com place() sobre a janela raiz.
#  Sem Toplevel → sem flash preto, sem borda preta.
# ─────────────────────────────────────────────
class ClickMenu:
    """
    Painel dropdown renderizado diretamente sobre a janela raiz.
    Abre/fecha com clique no botão da sidebar.
    """

    MENU_WIDTH = 240

    def __init__(self, root, titulo, itens, fontes, on_action):
        self._root      = root
        self._on_action = on_action

        self._frame = ctk.CTkFrame(
            root,
            width=self.MENU_WIDTH,
            fg_color=CORES["hover_menu_bg"],
            corner_radius=10,
            border_width=1,
            border_color=CORES["accent_soft"],
        )

        # Cabeçalho do menu
        header = ctk.CTkFrame(self._frame, fg_color="transparent", corner_radius=0)
        header.pack(fill="x", padx=10, pady=(10, 4))

        ctk.CTkLabel(
            header, text=titulo,
            font=fontes["subtitulo"],
            text_color=CORES["accent"],
            anchor="w"
        ).pack(side="left")

        # Separador
        ctk.CTkFrame(
            self._frame, height=1,
            fg_color=CORES["accent_soft"],
            corner_radius=0
        ).pack(fill="x", padx=0)

        # Itens — sem border_width para não criar linha preta
        for label, cmd in itens:
            btn = ctk.CTkButton(
                self._frame,
                text=f"  {label}",
                command=lambda c=cmd: self._fire(c),
                height=32,
                anchor="w",
                fg_color="transparent",
                hover_color=CORES["accent_soft"],
                text_color=CORES["text_primary"],
                font=fontes["pequena"],
                corner_radius=6,
                border_width=0,
            )
            btn.pack(fill="x", padx=6, pady=1)

        # Espaço inferior
        ctk.CTkFrame(self._frame, height=6, fg_color="transparent").pack()

    def _fire(self, cmd):
        self._on_action(cmd)

    def show_at(self, x: int, y: int):
        self._frame.place(x=x, y=y)
        self._frame.lift()
        self._frame.update_idletasks()
        # Ajuste se ultrapassar a altura da janela
        h  = self._frame.winfo_reqheight()
        wh = self._root.winfo_height()
        if y + h > wh - 10:
            self._frame.place(x=x, y=max(0, wh - h - 10))

    def winfo_rootx(self):  return self._frame.winfo_rootx()
    def winfo_rooty(self):  return self._frame.winfo_rooty()
    def winfo_width(self):  return self._frame.winfo_width()
    def winfo_height(self): return self._frame.winfo_height()

    def destroy(self):
        try:
            self._frame.place_forget()
            self._frame.destroy()
        except Exception:
            pass


# ─────────────────────────────────────────────
#  WIDGET: CARD DE ESTATÍSTICA
# ─────────────────────────────────────────────
class StatCard(ctk.CTkFrame):
    def __init__(self, parent, icon, label, fontes, **kwargs):
        super().__init__(
            parent,
            fg_color=CORES["bg_tertiary"],
            corner_radius=10,
            border_width=1,
            border_color=CORES["border"],
            **kwargs
        )
        self.FONTES = fontes

        ctk.CTkLabel(self, text=icon, font=ctk.CTkFont(size=17)).pack(pady=(10, 0))
        self._val = ctk.CTkLabel(
            self, text="—",
            font=self.FONTES["stat"],
            text_color=CORES["text_primary"]
        )
        self._val.pack()
        self._lbl = ctk.CTkLabel(
            self, text=label,
            font=self.FONTES["stat_label"],
            text_color=CORES["text_muted"]
        )
        self._lbl.pack(pady=(0, 10))

    def update(self, value: str, color: str = None):
        self._val.configure(text=value, text_color=color or CORES["text_primary"])

    def refresh_colors(self):
        self.configure(fg_color=CORES["bg_tertiary"], border_color=CORES["border"])
        self._val.configure(text_color=CORES["text_primary"])
        self._lbl.configure(text_color=CORES["text_muted"])


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
        self._badge_font = ctk.CTkFont(family="Segoe UI", size=10, weight="bold")
        self.set(estado, kwargs.get("text", ""))

    def set(self, estado: str, texto: str):
        fg, tc = self._COLORS.get(estado, self._COLORS["info"])
        self.configure(
            text=f"  {texto}  ",
            fg_color=fg,
            text_color=tc,
            corner_radius=6,
            font=self._badge_font,
        )


# ─────────────────────────────────────────────
#  APLICAÇÃO PRINCIPAL
# ─────────────────────────────────────────────
class SuporteTecnicoApp(ctk.CTk):

    SIDEBAR_W = 185
    HEADER_H  = 56
    STATS_H   = 110

    def __init__(self):
        super().__init__()

        self.withdraw()

        self.FONTES = {
            "titulo":     ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            "subtitulo":  ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            "corpo":      ctk.CTkFont(family="Segoe UI", size=12),
            "pequena":    ctk.CTkFont(family="Segoe UI", size=11),
            "console":    ctk.CTkFont(family="Consolas",  size=12),
            "badge":      ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            "stat":       ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            "stat_label": ctk.CTkFont(family="Segoe UI", size=10),
        }

        self.title("Suporte Técnico TI")
        self.configure(fg_color=CORES["bg_primary"])
        self.minsize(1000, 600)

        # Estado
        self._executando   = False
        self._tarefa_atual = None
        self._auto_scroll  = True
        self._sidebar_buttons: dict = {}
        self._grupo_ativo  = None
        self._log_queue: queue.Queue = queue.Queue()
        self._tema_atual   = "Dark"

        # Menu de click
        self._click_menu: ClickMenu | None = None
        self._menu_btn_ref: SidebarButton | None = None

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

        self.bind("<Button-1>", self._on_root_click, add="+")
        self.protocol("WM_DELETE_WINDOW", self._on_fechar_app)
        self.after(50, self._exibir_maximizado)

    def _exibir_maximizado(self):
        self.state("zoomed")
        self.deiconify()

    # ─────────────────────────────────────────────
    #  Fechar app
    # ─────────────────────────────────────────────
    def _on_fechar_app(self):
        if self._executando and self._tarefa_atual:
            self.log(
                f"⚠ Usuário fechou o aplicativo durante a execução de '{self._tarefa_atual}'. "
                "Operação interrompida — sistema liberado.",
                "WARN"
            )
            self._executando = False
            self._tarefa_atual = None
        self.destroy()

    # ── Layout principal ──────────────────────
    def _build_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._sidebar = ctk.CTkFrame(
            self, width=self.SIDEBAR_W,
            fg_color=CORES["sidebar_bg"],
            corner_radius=0,
            border_width=0,   # ← sem traço/borda
        )
        self._sidebar.grid(row=0, column=0, sticky="nsew")
        self._sidebar.grid_propagate(False)
        self._sidebar.grid_rowconfigure(99, weight=1)

        self._main = ctk.CTkFrame(self, fg_color=CORES["bg_primary"], corner_radius=0)
        self._main.grid(row=0, column=1, sticky="nsew")
        self._main.grid_rowconfigure(2, weight=1)
        self._main.grid_columnconfigure(0, weight=1)

    # ── Sidebar ───────────────────────────────
    def _build_sidebar(self):
        logo_frame = ctk.CTkFrame(
            self._sidebar, fg_color="transparent",
            height=self.HEADER_H, corner_radius=0, border_width=0
        )
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)

        ctk.CTkLabel(
            logo_frame,
            text="⚙  SUPORTE TI",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=CORES["accent"],
            anchor="w"
        ).place(relx=0.08, rely=0.5, anchor="w")

        self._sep_top = ctk.CTkFrame(
            self._sidebar, height=1,
            fg_color=CORES["separator"], corner_radius=0, border_width=0
        )
        self._sep_top.pack(fill="x")

        self._hostname_lbl = ctk.CTkLabel(
            self._sidebar,
            text=f"  🖥  {hostname()}",
            font=self.FONTES["pequena"],
            text_color=CORES["text_muted"],
            anchor="w"
        )
        self._hostname_lbl.pack(fill="x", padx=6, pady=(8, 2))

        self._admin_badge = StatusBadge(
            self._sidebar,
            estado="online" if is_admin() else "warn",
            text="✔ Admin" if is_admin() else "⚠ Sem Priv."
        )
        self._admin_badge.pack(padx=10, pady=(0, 8), anchor="w")

        self._sep_mid = ctk.CTkFrame(
            self._sidebar, height=1,
            fg_color=CORES["separator"], corner_radius=0, border_width=0
        )
        self._sep_mid.pack(fill="x", pady=2)

        # ── Grupos com menu por clique ──
        grupos = [
            ("REDE",        "🌐", self._itens_rede),
            ("SISTEMA",     "💻", self._itens_sistema),
            ("IMPRESSÃO",   "🖨", self._itens_impressao),
            ("USUÁRIOS",    "👤", self._itens_usuarios),
            ("SERVIÇOS",    "⚙",  self._itens_servicos),
            ("DIAGNÓSTICO", "🔬", self._itens_diagnostico),
            ("FERRAMENTAS", "🛠", self._itens_ferramentas),
            ("ATIVAÇÃO",    "🔑", self._itens_ativacao),
        ]

        for nome, icone, itens_fn in grupos:
            btn = SidebarButton(
                self._sidebar, icon=icone, label=nome,
                fontes=self.FONTES,
            )
            btn.pack(fill="x", padx=6, pady=1)
            self._sidebar_buttons[nome] = btn

            titulo = f"{icone}  {nome}"
            self._setup_click_btn(btn, nome, titulo, itens_fn)

        # Espaçador + tema
        ctk.CTkFrame(
            self._sidebar,
            fg_color="transparent",
            height=170,
            corner_radius=0,
            border_width=0
        ).pack(fill="x")

        self._sep_bottom = ctk.CTkFrame(
            self._sidebar, height=1,
            fg_color=CORES["separator"], corner_radius=0, border_width=0
        )
        self._sep_bottom.pack(fill="x")

        tema_frame = ctk.CTkFrame(
            self._sidebar, fg_color="transparent", corner_radius=0, border_width=0
        )
        tema_frame.pack(fill="x", padx=8, pady=8)
        ctk.CTkLabel(
            tema_frame, text="🎨",
            font=self.FONTES["pequena"],
            text_color=CORES["text_muted"]
        ).pack(side="left")
        
        self._tema_menu = ctk.CTkOptionMenu(
            tema_frame,
            values=["Dark", "Light", "Azul", "Verde"],
            command=self._mudar_tema,
            width=80,
            height=30,
            font=self.FONTES["pequena"],
            fg_color=CORES["bg_tertiary"],
            button_color=CORES["accent"],
            button_hover_color=CORES["accent_hover"],

            text_color=CORES["text_primary"],
            dropdown_text_color=CORES["text_primary"],
            dropdown_fg_color=CORES["bg_secondary"],
        )
        self._tema_menu.set("Dark")
        self._tema_menu.pack(side="right")

    def _setup_click_btn(self, btn, nome, titulo, itens_fn):
        """Configura hover visual + abertura/fechamento por clique."""

        def on_click(e=None):
            # Toggle: se já está aberto para este botão, fecha
            if self._grupo_ativo == nome and self._click_menu:
                self._close_menu_now()
                return
            self._open_menu(btn, nome, titulo, itens_fn())

        def on_enter(e=None):
            btn.on_hover_enter()

        def on_leave(e=None):
            btn.on_hover_leave()

        # Bindings no frame e nos filhos internos
        for widget in [btn, btn._icon_lbl, btn._text_lbl, btn._arrow_lbl]:
            widget.bind("<Button-1>", on_click, add="+")
            widget.bind("<Enter>",    on_enter, add="+")
            widget.bind("<Leave>",    on_leave, add="+")

    # ── Menu de clique: open / close ──────────
    def _open_menu(self, btn, nome, titulo, itens):
        self._close_menu_now()

        # Coordenadas relativas à janela raiz
        screen_x = btn.winfo_rootx() + btn.winfo_width() + 4
        screen_y = btn.winfo_rooty()
        root_x   = screen_x - self.winfo_rootx()
        root_y   = screen_y - self.winfo_rooty()

        self._click_menu = ClickMenu(
            self, titulo, itens, self.FONTES,
            on_action=self._on_menu_action,
        )
        self._click_menu.show_at(root_x, root_y)
        self._menu_btn_ref = btn

        # Desativa o botão anterior
        if self._grupo_ativo and self._grupo_ativo != nome:
            try:
                self._sidebar_buttons[self._grupo_ativo].set_active(False)
            except Exception:
                pass

        self._grupo_ativo = nome
        btn.set_active(True)

    def _on_menu_action(self, cmd):
        self._close_menu_now()
        cmd()

    def _close_menu_now(self):
        if self._click_menu:
            try:
                self._click_menu.destroy()
            except Exception:
                pass
            self._click_menu    = None
            self._menu_btn_ref  = None

        if self._grupo_ativo:
            try:
                self._sidebar_buttons[self._grupo_ativo].set_active(False)
            except Exception:
                pass
            self._grupo_ativo = None

    def _on_root_click(self, event):
        """Fecha o menu ao clicar fora dele."""
        if not self._click_menu:
            return
        try:
            mx = self._click_menu.winfo_rootx()
            my = self._click_menu.winfo_rooty()
            mw = self._click_menu.winfo_width()
            mh = self._click_menu.winfo_height()
            px, py = event.x_root, event.y_root
            # Não fecha se clicou dentro do menu
            if mx <= px <= mx + mw and my <= py <= my + mh:
                return
            # Não fecha se clicou num botão da sidebar (ele trata o toggle)
            widget = event.widget
            while widget:
                if isinstance(widget, SidebarButton):
                    return
                try:
                    widget = widget.master
                except Exception:
                    break
            self._close_menu_now()
        except Exception:
            pass

    # ── Header ────────────────────────────────
    def _build_header(self):
        self._header_frame = ctk.CTkFrame(
            self._main, height=self.HEADER_H,
            fg_color=CORES["bg_secondary"],
            corner_radius=0
        )
        self._header_frame.grid(row=0, column=0, sticky="ew")
        self._header_frame.grid_propagate(False)

        self._header_title = ctk.CTkLabel(
            self._header_frame, text="Painel de Suporte",
            font=self.FONTES["titulo"],
            text_color=CORES["text_primary"]
        )
        self._header_title.pack(side="left", padx=20)

        self._hora_lbl = ctk.CTkLabel(
            self._header_frame, text="",
            font=self.FONTES["pequena"],
            text_color=CORES["text_muted"]
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
        self._stats_bar = ctk.CTkFrame(
            self._main, height=self.STATS_H,
            fg_color=CORES["bg_secondary"],
            corner_radius=0
        )
        self._stats_bar.grid(row=1, column=0, sticky="ew")
        self._stats_bar.grid_propagate(False)
        self._stats_bar.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="stat_col")
        self._stats_bar.grid_rowconfigure(0, weight=1)

        self._cpu_card  = StatCard(self._stats_bar, "🔄", "CPU",   self.FONTES)
        self._ram_card  = StatCard(self._stats_bar, "🧠", "RAM",   self.FONTES)
        self._disk_card = StatCard(self._stats_bar, "💾", "DISCO", self.FONTES)
        self._net_card  = StatCard(self._stats_bar, "🌐", "REDE",  self.FONTES)

        cards = (self._cpu_card, self._ram_card, self._disk_card, self._net_card)
        for i, card in enumerate(cards):
            card.grid(row=0, column=i, padx=(8 if i == 0 else 4, 4 if i < 3 else 8),
                      pady=8, sticky="nsew")

    # ── Área de log ───────────────────────────
    def _build_log_area(self):
        self._log_outer = ctk.CTkFrame(
            self._main,
            fg_color=CORES["bg_secondary"],
            corner_radius=12
        )
        self._log_outer.grid(row=2, column=0, sticky="nsew", padx=16, pady=(12, 4))
        self._log_outer.grid_rowconfigure(1, weight=1)
        self._log_outer.grid_columnconfigure(0, weight=1)

        toolbar = ctk.CTkFrame(self._log_outer, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 0))

        self._log_title = ctk.CTkLabel(
            toolbar, text="📋  Log de Execução",
            font=self.FONTES["subtitulo"],
            text_color=CORES["text_secondary"]
        )
        self._log_title.pack(side="left")

        self._toolbar_btns = []
        for txt, cmd in (
            ("⬇ Exportar", self._exportar_log),
            ("🗑 Limpar",  self._limpar_log),
        ):
            b = ctk.CTkButton(
                toolbar, text=txt, command=cmd,
                width=90, height=26,
                font=self.FONTES["pequena"],
                fg_color=CORES["bg_tertiary"],
                hover_color=CORES["border"],
                text_color=CORES["text_secondary"],
                border_width=1, border_color=CORES["border"],
                corner_radius=6
            )
            b.pack(side="right", padx=4)
            self._toolbar_btns.append(b)

        self._scroll_var = ctk.BooleanVar(value=True)
        self._auto_scroll_sw = ctk.CTkSwitch(
            toolbar, text="Auto-scroll",
            variable=self._scroll_var,
            font=self.FONTES["pequena"],
            text_color=CORES["text_muted"],
            button_color=CORES["accent"],
            progress_color=CORES["accent_soft"],
            onvalue=True, offvalue=False,
            width=44, height=20,
            command=lambda: setattr(self, "_auto_scroll", self._scroll_var.get())
        )
        self._auto_scroll_sw.pack(side="right", padx=8)

        self._log_text = ctk.CTkTextbox(
            self._log_outer,
            font=self.FONTES["console"],
            fg_color=CORES["bg_primary"],
            text_color=CORES["text_primary"],
            corner_radius=8,
            state="disabled",
            wrap="word",
        )
        self._log_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self._reconfigure_log_tags()

    def _reconfigure_log_tags(self):
        self._log_text.tag_config("ts",   foreground=CORES["text_muted"])
        self._log_text.tag_config("ok",   foreground=CORES["success"])
        self._log_text.tag_config("erro", foreground=CORES["danger"])
        self._log_text.tag_config("warn", foreground=CORES["warning"])
        self._log_text.tag_config("info", foreground="#93c5fd")
        self._log_text.tag_config("sep",  foreground=CORES["text_muted"])
        self._log_text.tag_config("cmd",  foreground="#c084fc")

    # ── Status bar ────────────────────────────
    def _build_status_bar(self):
        self._status_bar = ctk.CTkFrame(
            self._main, height=30,
            fg_color=CORES["bg_secondary"],
            corner_radius=0
        )
        self._status_bar.grid(row=3, column=0, sticky="ew")
        self._status_bar.grid_propagate(False)

        self._status_lbl = ctk.CTkLabel(
            self._status_bar, text="  ✔  Pronto",
            font=self.FONTES["pequena"],
            text_color=CORES["success"],
            anchor="w"
        )
        self._status_lbl.pack(side="left", padx=10)

        self._progress = ctk.CTkProgressBar(
            self._status_bar, width=180, height=6,
            progress_color=CORES["accent"],
            fg_color=CORES["bg_tertiary"],
            corner_radius=3
        )
        self._progress.pack(side="right", padx=16, pady=8)
        self._progress.set(0)

    # ─────────────────────────────────────────────
    #  LISTAS DE ITENS POR GRUPO
    # ─────────────────────────────────────────────
    def _itens_rede(self):
        return [
            ("Status de Conexão",   self._rede_status),
            ("Redes Wi-Fi Salvas",  self._rede_wifi_salvas),
            ("IP / MAC / DNS",      lambda: self._cmd("ipconfig /all", "IP/MAC/DNS")),
            ("Flush DNS",           lambda: self._cmd("ipconfig /flushdns", "Flush DNS")),
            ("Renovar IP",          self._rede_renovar_ip),
            ("Sincronizar NTP",     self._rede_ntp),
            ("Traceroute 8.8.8.8",  lambda: self._cmd("tracert 8.8.8.8", "Traceroute")),
            ("Diagnóstico de Rede", self._rede_diagnostico),
        ]

    def _itens_sistema(self):
        return [
            ("Limpar Temporários",   self._sis_limpar_temp),
            ("Limpeza Avançada",     self._sis_limpeza_completa),
            ("SFC Scan",             lambda: self._cmd("sfc /scannow", "SFC Scan")),
            ("DISM RestoreHealth",   lambda: self._cmd("DISM /Online /Cleanup-Image /RestoreHealth", "DISM")),
            ("Informações Hardware", lambda: self._cmd("systeminfo", "Hardware Info")),
            ("Política de Grupo",    lambda: self._cmd("gpupdate /force", "GPUpdate")),
        ]

    def _itens_impressao(self):
        return [
            ("Reset Spooler",         self._imp_resetar_spooler),
            ("Ver Fila de Impressão", lambda: self._cmd(
                "explorer shell:::{2227A280-3AEA-1069-A2DE-08002B30309D}", "Fila")),
            ("Gerenciar Impressoras", lambda: self._cmd("control printers", "Impressoras")),
            ("Reinstalar Driver",     self._imp_reinstalar_driver),
        ]

    def _itens_usuarios(self):
        return [
            ("Desbloquear Conta",  self._usr_desbloquear),
            ("Alterar Senha",      self._usr_senha),
            ("Logoff Forçado",     self._usr_logoff),
            ("Adicionar ao Admin", self._usr_add_admin),
            ("Listar Usuários",    lambda: self._cmd("net user", "Listar Usuários")),
        ]

    def _itens_servicos(self):
        return [
            ("Top 5 Processos CPU",  self._svc_processos_pesados),
            ("Top 5 Processos RAM",  self._svc_processos_ram),
            ("Gerenciador de Serv.", lambda: self._cmd("services.msc", "Serviços")),
            ("Event Viewer",         lambda: self._cmd("eventvwr.msc", "Event Viewer")),
            ("Eventos Críticos",     self._svc_eventos_criticos),
        ]

    def _itens_diagnostico(self):
        return [
            ("Saúde do Sistema",   self._diag_saude),
            ("Verificar Drivers",  self._diag_drivers),
            ("Teste de Memória",   lambda: self._cmd("mdsched", "Memória")),
            ("SMART de Disco",     self._diag_smart),
            ("Tempo de Boot",      self._diag_boot_time),
        ]

    def _itens_ferramentas(self):
        return [
            ("Painel de Controle", lambda: self._cmd("control", "Painel")),
            ("Gerenc. de Tarefas", lambda: self._cmd("taskmgr", "TaskMgr")),
            ("Editor do Registro", lambda: self._cmd("regedit", "Regedit")),
            ("Gerar Relatório",    self._fer_relatorio),
            ("Abrir Log Externo",  self._fer_abrir_log),
        ]

    def _itens_ativacao(self):
        return [
            ("Ativar Windows / Office", self._ativar_windows_office),
        ]

    # ─────────────────────────────────────────────
    #  LOG ENGINE
    # ─────────────────────────────────────────────
    def log(self, msg: str, nivel: str = "INFO"):
        self._log_queue.put((msg, nivel))

    def _processar_log_queue(self):
        try:
            for _ in range(10):
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
            ts_start = self._log_text.index("end-1c")
            self._log_text.insert("end", f"[{ts}] ")
            ts_end = self._log_text.index("end-1c")
            self._log_text.tag_add("ts", ts_start, ts_end)

            nivel_start = ts_end
            self._log_text.insert("end", f"{icone} ")
            nivel_end = self._log_text.index("end-1c")
            self._log_text.tag_add(tag, nivel_start, nivel_end)

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
        self.log(
            f"SISTEMA DE SUPORTE TI  |  {hostname()}  |  {datetime.now().strftime('%d/%m/%Y')}",
            "INFO"
        )
        self.log(
            f"Modo Admin: {'✔ Ativo' if is_admin() else '✖ Inativo — algumas funções podem falhar'}",
            "OK" if is_admin() else "WARN"
        )
        self.log("Clique nos grupos na sidebar para ver as ações disponíveis.", "INFO")
        self.log("SEP", "SEP")

    # ─────────────────────────────────────────────
    #  THREADING
    # ─────────────────────────────────────────────
    def _run(self, func, nome_op: str = "Operação"):
        if self._executando:
            self.log(
                f"⛔ Aguarde a conclusão de '{self._tarefa_atual}' antes de iniciar outra função.",
                "WARN"
            )
            return

        def wrapper():
            self._executando   = True
            self._tarefa_atual = nome_op
            self._set_status(f"⏳  {nome_op}...", CORES["warning"])
            self._progress.configure(mode="indeterminate")
            self._progress.start()
            try:
                func()
            except Exception as e:
                self.log(f"Erro inesperado: {e}", "ERRO")
            finally:
                self._executando   = False
                self._tarefa_atual = None
                self._progress.stop()
                self._progress.configure(mode="determinate")
                self._progress.set(0)
                self._set_status("✔  Pronto", CORES["success"])

        threading.Thread(target=wrapper, daemon=True).start()

    def _set_status(self, texto: str, cor: str = None):
        self.after(0, lambda: self._status_lbl.configure(
            text=f"  {texto}", text_color=cor or CORES["text_primary"]
        ))

    def _cmd(self, cmd: str, nome: str = None):
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
        cpu  = psutil.cpu_percent(interval=None)
        ram  = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent

        def _cor(val):
            if val >= 90: return CORES["danger"]
            if val >= 70: return CORES["warning"]
            return CORES["success"]

        self._cpu_card.update(f"{cpu:.0f}%",  _cor(cpu))
        self._ram_card.update(f"{ram:.0f}%",  _cor(ram))
        self._disk_card.update(f"{disk:.0f}%", _cor(disk))

        # Card REDE: exibe ONLINE/OFFLINE com base em ping assíncrono
        # Atualiza a cada 10s para não sobrecarregar
        self._net_tick = getattr(self, "_net_tick", 0) + 1
        if self._net_tick >= 10 or not hasattr(self, "_net_status_cache"):
            self._net_tick = 0
            threading.Thread(target=self._atualizar_net_card, daemon=True).start()

        self.after(1000, self._atualizar_stats)

    def _atualizar_net_card(self):
        """Verifica conectividade em background e atualiza o card REDE."""
        try:
            r = subprocess.run(
                "ping -n 1 -w 1500 8.8.8.8", shell=True,
                capture_output=True, creationflags=CREATE_NO_WINDOW
            )
            online = r.returncode == 0
            if online:
                # Extrai latência da linha de resumo
                raw = r.stdout.decode("cp1252", errors="replace")
                ms = "—"
                for linha in raw.splitlines():
                    m = re.search(r"[=<]\s*(\d+)\s*ms", linha)
                    if m:
                        ms = f"{m.group(1)}ms"
                        break
                texto = f"ONLINE  {ms}"
                cor   = CORES["success"]
            else:
                texto = "OFFLINE"
                cor   = CORES["danger"]
            self._net_status_cache = (texto, cor)
        except Exception:
            self._net_status_cache = ("N/D", CORES["text_muted"])

        texto, cor = self._net_status_cache
        self.after(0, lambda: self._net_card.update(texto, cor))

    # ─────────────────────────────────────────────
    #  IMPLEMENTAÇÕES — REDE
    # ─────────────────────────────────────────────
    @staticmethod
    def _parse_ssid(texto: str) -> str:
        """
        Extrai o SSID do output de 'netsh wlan show interfaces'.
        Suporta PT-BR ("SSID") e EN ("SSID") e qualquer quantidade de espaços/tabs.
        Ignora linhas com BSSID.
        """
        for linha in texto.splitlines():
            linha_strip = linha.strip()
            # Ignora BSSID
            if "BSSID" in linha_strip:
                continue
            # Aceita "SSID" seguido de espaços, dois-pontos e o valor
            m = re.match(r"^SSID\s*:\s*(.+)$", linha_strip, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return "—"

    @staticmethod
    def _netsh(args: str) -> str:
        """
        Roda netsh e decodifica corretamente.
        Windows BR moderno usa CP1252 (ANSI); sistemas mais antigos CP850.
        Tenta na ordem: cp1252 -> cp850 -> mbcs -> utf-8.
        """
        try:
            r = subprocess.run(
                f"netsh {args}", shell=True,
                capture_output=True, creationflags=CREATE_NO_WINDOW
            )
            raw = r.stdout
        except Exception:
            return ""
        for enc in ("cp1252", "cp850", "mbcs", "utf-8"):
            try:
                return raw.decode(enc, errors="strict")
            except (UnicodeDecodeError, LookupError):
                continue
        return raw.decode("utf-8", errors="replace")

    def _rede_status(self):
        def run():
            self.log("─── Status de Conexão de Rede ───", "SEP")

            # ── Teste de conectividade básica ──
            ping1 = subprocess.run(
                "ping -n 1 -w 2000 8.8.8.8", shell=True,
                capture_output=True, creationflags=CREATE_NO_WINDOW
            )
            internet = ping1.returncode == 0
            self.log(f"Internet (8.8.8.8)  : {'ONLINE' if internet else 'OFFLINE'}",
                     "OK" if internet else "ERRO")

            # ── Resolução DNS ──
            dns_res = subprocess.run(
                "ping -n 1 -w 2000 google.com", shell=True,
                capture_output=True, creationflags=CREATE_NO_WINDOW
            )
            dns_ok = dns_res.returncode == 0
            self.log(f"Resolução DNS       : {'OK' if dns_ok else 'FALHA'}",
                     "OK" if dns_ok else "ERRO")

            # ── Tipo de conexão e SSID ──
            iface_txt = self._netsh("wlan show interfaces")
            ssid = self._parse_ssid(iface_txt)
            eh_wifi = ssid != "—"
            tipo = "Wi-Fi" if eh_wifi else "Cabo (Ethernet)"
            self.log(f"Tipo de conexão     : {tipo}")
            if eh_wifi:
                self.log(f"SSID                : {ssid}")

                # Sinal Wi-Fi
                for linha in iface_txt.splitlines():
                    ls = linha.strip()
                    if re.match(r"^Sinal\s*:|^Signal\s*:", ls, re.IGNORECASE):
                        sinal = ls.split(":", 1)[1].strip()
                        self.log(f"Sinal               : {sinal}")
                        break

            # ── IP local ──
            try:
                import socket
                ip_local = socket.gethostbyname(socket.gethostname())
                self.log(f"IP local            : {ip_local}")
            except Exception:
                pass

            # ── Latência média (4 pings) ──
            if internet:
                ping4 = subprocess.run(
                    "ping -n 4 -w 2000 8.8.8.8", shell=True,
                    capture_output=True, creationflags=CREATE_NO_WINDOW
                )
                raw4 = ping4.stdout.decode("cp1252", errors="replace")
                for l in raw4.splitlines():
                    # PT-BR: "Média = Xms"  |  EN: "Average = Xms"
                    if re.search(r"(M[eé]dia|Average)\s*=", l, re.IGNORECASE):
                        self.log(f"Latência média      : {l.strip()}")
                        break

        self._run(run, "Status de Rede")

    def _rede_wifi_salvas(self):
        def run():
            self.log("Listando perfis Wi-Fi salvos...")

            # Usa PowerShell para evitar problemas de encoding do netsh
            # (netsh usa CP1252/CP850 que pode corromper nomes acentuados)
            ps_script = (
                "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8;"
                "(netsh wlan show profiles) -split '\n' | "
                "ForEach-Object { $_ } | "
                "Out-String"
            )
            b64 = base64.b64encode(ps_script.encode("utf-16le")).decode()
            r = subprocess.run(
                f"powershell -NoProfile -ExecutionPolicy Bypass -EncodedCommand {b64}",
                shell=True, capture_output=True,
                creationflags=CREATE_NO_WINDOW
            )
            perfis_txt = r.stdout.decode("utf-8", errors="replace")

            # Se PS falhou, tenta netsh direto com múltiplos encodings
            if not perfis_txt.strip():
                perfis_txt = self._netsh("wlan show profiles")

            # Extrai nomes: a linha pode ter qualquer rótulo dependendo do idioma do SO,
            # mas SEMPRE termina com  ": <nome da rede>"  após dois pontos.
            # Estratégia: pega todas as linhas que contêm " : " e não são cabeçalhos/vazias,
            # filtrando apenas as linhas de perfil (que aparecem indentadas com espaço).
            perfis = []
            for linha in perfis_txt.splitlines():
                # Linhas de perfil são sempre indentadas e têm formato "  Rótulo : Valor"
                if not linha.startswith(" ") and not linha.startswith("	"):
                    continue
                if ":" not in linha:
                    continue
                partes = linha.split(":", 1)
                rotulo = partes[0].strip().lower()
                valor  = partes[1].strip()
                if not valor:
                    continue
                # Filtra rótulos conhecidos de perfil em PT-BR e EN
                # (evita capturar outras linhas como "Interface: Wi-Fi")
                eh_perfil = any(p in rotulo for p in (
                    "perfil", "profile", "usu", "user"
                ))
                if eh_perfil:
                    perfis.append(valor)

            # Último fallback: regex clássico sem depender de rótulo
            if not perfis:
                perfis = re.findall(r":\s+([^\r\n]+)", perfis_txt)
                # Remove linhas que são claramente cabeçalho/interface
                perfis = [p.strip() for p in perfis
                          if p.strip() and not re.match(
                              r"(Interface|Adaptador|SSID|BSSID|Sinal|Signal|Autentica|Cifra|Tipo|Mode)", 
                              p.strip(), re.IGNORECASE
                          )]

            perfis = list(dict.fromkeys(p for p in perfis if p))  # dedup mantendo ordem

            # SSID atual via netsh interfaces (também via PS para encoding correto)
            iface_txt  = self._netsh("wlan show interfaces")
            ssid_atual = self._parse_ssid(iface_txt)

            if perfis:
                for p in perfis:
                    conectado = (p == ssid_atual)
                    sufixo = "  ◀ CONECTADO" if conectado else ""
                    self.log(f"  {p}{sufixo}", "OK" if conectado else "INFO")
                self.log(f"Total: {len(perfis)} rede(s) salva(s).")
                if ssid_atual != "—":
                    self.log(f"Rede atual: {ssid_atual}", "OK")
            else:
                self.log("Nenhum perfil Wi-Fi encontrado (sem adaptador Wi-Fi ou sem redes salvas).", "WARN")

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

            gateway = None
            try:
                gw_res = subprocess.run(
                    'powershell -NoProfile -Command '
                    '"(Get-NetRoute -DestinationPrefix \'0.0.0.0/0\' '
                    '| Sort-Object RouteMetric | Select-Object -First 1).NextHop"',
                    shell=True, capture_output=True, text=True,
                    encoding="utf-8", errors="ignore",
                    creationflags=CREATE_NO_WINDOW
                )
                gw_out = gw_res.stdout.strip()
                if gw_out and re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", gw_out):
                    gateway = gw_out
            except Exception:
                pass

            if not gateway:
                try:
                    ipconf = subprocess.run(
                        "ipconfig", shell=True, capture_output=True, text=True,
                        encoding="utf-8", errors="ignore",
                        creationflags=CREATE_NO_WINDOW
                    ).stdout
                    for line in ipconf.split("\n"):
                        if "Gateway" in line or "gateway" in line:
                            parts = line.split(":")
                            if len(parts) > 1:
                                candidate = parts[-1].strip()
                                if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", candidate):
                                    gateway = candidate
                                    break
                except Exception:
                    pass

            if gateway:
                self.log(f"Gateway detectado: {gateway}", "INFO")
            else:
                gateway = "192.168.1.1"
                self.log(f"Gateway não detectado automaticamente. Usando: {gateway}", "WARN")

            testes = [
                (f"Gateway ({gateway})", f"ping -n 2 {gateway}"),
                ("DNS 8.8.8.8",          "ping -n 2 8.8.8.8"),
                ("Google.com",           "ping -n 2 google.com"),
            ]
            for nome_teste, cmd in testes:
                r = subprocess.run(
                    cmd, shell=True, capture_output=True,
                    creationflags=CREATE_NO_WINDOW
                )
                self.log(
                    f"{nome_teste:22}: {'OK' if r.returncode == 0 else 'FALHA'}",
                    "OK" if r.returncode == 0 else "ERRO"
                )

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
            subprocess.run(
                "taskkill /f /im explorer.exe", shell=True,
                capture_output=True, creationflags=CREATE_NO_WINDOW
            )
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
            subprocess.run(
                "Dism.exe /Online /Cleanup-Image /StartComponentCleanup",
                shell=True, creationflags=CREATE_NO_WINDOW
            )
            self.log("Limpeza profunda concluída.", "OK")

        self._run(run, "Limpeza Avançada")

    def _run_ps_encoded(self, script: str):
        b64 = base64.b64encode(script.encode("utf-16le")).decode()
        subprocess.run(
            f"powershell -NoProfile -ExecutionPolicy Bypass -EncodedCommand {b64}",
            shell=True, creationflags=CREATE_NO_WINDOW
        )

    # ─────────────────────────────────────────────
    #  IMPLEMENTAÇÕES — IMPRESSÃO
    # ─────────────────────────────────────────────
    def _imp_resetar_spooler(self):
        def run():
            self.log("Parando serviço Spooler...")
            subprocess.run("net stop spooler", shell=True, creationflags=CREATE_NO_WINDOW)
            self.log("Limpando fila de impressão...")
            subprocess.run(
                "del /Q /F /S %systemroot%\\System32\\spool\\PRINTERS\\*",
                shell=True, creationflags=CREATE_NO_WINDOW
            )
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
    def _input(self, titulo: str, prompt: str):
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
        if u:
            self._cmd(f"logoff {u}", "Logoff Forçado")

    def _usr_add_admin(self):
        u = self._input("Adicionar Administrador", "Nome do usuário:")
        if u:
            self._cmd(f"net localgroup administrators {u} /add", "Add Admin")

    # ─────────────────────────────────────────────
    #  IMPLEMENTAÇÕES — SERVIÇOS
    # ─────────────────────────────────────────────
    def _svc_processos_pesados(self):
        def run():
            self.log("Coletando uso de CPU (aguarde ~1s)...")
            procs_obj = []
            for p in psutil.process_iter(["name", "pid"]):
                try:
                    p.cpu_percent(interval=None)
                    procs_obj.append(p)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            time.sleep(1.0)
            procs = []
            for p in procs_obj:
                try:
                    cpu = p.cpu_percent(interval=None)
                    procs.append((p.info["name"], p.info["pid"], cpu))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            top = sorted(procs, key=lambda x: x[2], reverse=True)[:5]
            self.log("Top 5 por CPU:")
            for nome, pid, cpu in top:
                self.log(
                    f"  {nome:<30} PID:{pid:<6} CPU:{cpu:.1f}%",
                    "WARN" if cpu > 50 else "INFO"
                )

        self._run(run, "Processos CPU")

    def _svc_processos_ram(self):
        def run():
            procs = []
            for p in psutil.process_iter(["name", "pid", "memory_info"]):
                try:
                    mb = p.info["memory_info"].rss / 1024 / 1024
                    procs.append((p.info["name"], p.info["pid"], mb))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            top = sorted(procs, key=lambda x: x[2], reverse=True)[:5]
            self.log("Top 5 por RAM:")
            for nome, pid, mb in top:
                self.log(
                    f"  {nome:<30} PID:{pid:<6} RAM:{mb:.0f} MB",
                    "WARN" if mb > 500 else "INFO"
                )

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
            score   = 100
            alertas = []

            p1 = subprocess.run(
                "ping -n 1 8.8.8.8", shell=True,
                capture_output=True, creationflags=CREATE_NO_WINDOW
            )
            if p1.returncode != 0:
                score -= 30
                alertas.append("Sem acesso à internet")

            p2 = subprocess.run(
                "nslookup google.com", shell=True,
                capture_output=True, text=True,
                creationflags=CREATE_NO_WINDOW
            )
            if "Address" not in p2.stdout:
                score -= 20
                alertas.append("Falha na resolução DNS")

            cpu = psutil.cpu_percent(interval=0.5)
            if cpu > 90:
                score -= 15
                alertas.append(f"CPU crítico: {cpu:.0f}%")

            ram = psutil.virtual_memory().percent
            if ram > 90:
                score -= 15
                alertas.append(f"RAM crítica: {ram:.0f}%")

            disk = psutil.disk_usage("/").percent
            if disk > 90:
                score -= 10
                alertas.append(f"Disco quase cheio: {disk:.0f}%")

            nivel = "OK" if score >= 80 else ("WARN" if score >= 50 else "ERRO")
            self.log(f"RESULTADO: {score}/100", nivel)
            if alertas:
                for a in alertas:
                    self.log(f"  ⚠ {a}", "WARN")
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
            boot   = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot
            h, r   = divmod(int(uptime.total_seconds()), 3600)
            m, s   = divmod(r, 60)
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
                f.write("RELATÓRIO DE SUPORTE TI\n")
                f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Host: {hostname()}\n")
                f.write("=" * 60 + "\n\n")
                res = subprocess.run(
                    "systeminfo", shell=True,
                    capture_output=True, text=True,
                    encoding="utf-8", errors="ignore",
                    creationflags=CREATE_NO_WINDOW
                )
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
    #  ATIVAÇÃO WINDOWS / OFFICE (MAS)
    # ─────────────────────────────────────────────
    def _ativar_windows_office(self):
        def run():
            self.log("Iniciando ativação do Windows/Office...", "INFO")
            self.log("Script: irm https://get.activated.win | iex", "CMD")
            self.log("Abrindo janela do PowerShell — siga as instruções na tela.", "WARN")
            try:
                subprocess.Popen(
                    'powershell -NoProfile -ExecutionPolicy Bypass -Command '
                    '"irm https://get.activated.win | iex"',
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                )
                self.log("Script de ativação aberto em janela separada.", "OK")
                self.log("Aguarde a conclusão na janela do PowerShell.", "INFO")
            except Exception as e:
                self.log(f"Erro ao iniciar ativação: {e}", "ERRO")

        self._run(run, "Ativar Windows/Office")

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
        global CORES

        ctk_mode = {"Dark": "Dark", "Light": "Light", "Azul": "Dark", "Verde": "Dark"}.get(tema, "Dark")
        ctk.set_appearance_mode(ctk_mode)

        if tema in TEMAS_CORES:
            CORES = TEMAS_CORES[tema]

        self._tema_atual = tema
        self._aplicar_tema_widgets()
        self.log(f"Tema alterado para: {tema}", "INFO")

    def _aplicar_tema_widgets(self):
        self.configure(fg_color=CORES["bg_primary"])

        # Sidebar
        self._sidebar.configure(fg_color=CORES["sidebar_bg"])
        self._sep_top.configure(fg_color=CORES["separator"])
        self._sep_mid.configure(fg_color=CORES["separator"])
        self._sep_bottom.configure(fg_color=CORES["separator"])
        self._hostname_lbl.configure(text_color=CORES["text_muted"])

        for btn in self._sidebar_buttons.values():
            btn.refresh_colors()

        self._tema_menu.configure(
            fg_color=CORES["bg_tertiary"],
            button_color=CORES["accent"],
            button_hover_color=CORES["accent_hover"],
            text_color=CORES["text_primary"],
            dropdown_text_color=CORES["text_primary"],
            dropdown_fg_color=CORES["bg_secondary"],
        )

        # Main
        self._main.configure(fg_color=CORES["bg_primary"])

        # Header
        self._header_frame.configure(fg_color=CORES["bg_secondary"])
        self._header_title.configure(text_color=CORES["text_primary"])
        self._hora_lbl.configure(text_color=CORES["text_muted"])

        # Stats
        self._stats_bar.configure(fg_color=CORES["bg_secondary"])
        for card in (self._cpu_card, self._ram_card, self._disk_card, self._net_card):
            card.refresh_colors()

        # Log
        self._log_outer.configure(fg_color=CORES["bg_secondary"])
        self._log_title.configure(text_color=CORES["text_secondary"])
        self._log_text.configure(
            fg_color=CORES["bg_primary"],
            text_color=CORES["text_primary"]
        )
        self._reconfigure_log_tags()

        for b in self._toolbar_btns:
            b.configure(
                fg_color=CORES["bg_tertiary"],
                hover_color=CORES["border"],
                text_color=CORES["text_secondary"],
                border_color=CORES["border"],
            )
        self._auto_scroll_sw.configure(
            text_color=CORES["text_muted"],
            button_color=CORES["accent"],
            progress_color=CORES["accent_soft"],
        )

        # Status bar
        self._status_bar.configure(fg_color=CORES["bg_secondary"])
        self._progress.configure(
            progress_color=CORES["accent"],
            fg_color=CORES["bg_tertiary"],
        )

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
    # Oculta a janela do console (tela preta tipo CMD) imediatamente
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE = 0
    except Exception:
        pass

    if is_admin():
        app = SuporteTecnicoApp()
        app.mainloop()
    else:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )