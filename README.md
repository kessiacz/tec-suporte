# 🛠️ Tec-Suporte — Painel de Suporte Técnico para Windows

> Ferramenta desktop desenvolvida em Python para automatizar tarefas de suporte técnico, manutenção e diagnóstico no Windows — do script de terminal até uma interface gráfica completa.

---

## 📌 Sobre o Projeto

O **tec-suporte** nasceu da necessidade de agilizar tarefas repetitivas do dia a dia do suporte técnico de TI: flush de DNS, reset do spooler, limpeza de temporários, desbloqueio de usuários, diagnóstico de rede...

O projeto evoluiu ao longo de **4 versões**, partindo de uma CLI simples até um painel desktop com interface profissional, monitoramento em tempo real e múltiplos temas visuais.

---

## 🗂️ Versões do Projeto

### v1 — CLI (Linha de Comando)
- **Arquivo:** `tec-suporte-v1.py` / `dist/tec-suporte-v1.exe`
- Interface de terminal com menus numéricos interativos
- Leve, direto e sem dependências gráficas
- Ideal para execução remota via SSH ou em máquinas sem ambiente gráfico

**Estrutura de menus:**
- **Manutenção** — limpeza e otimização rápida
- **Sistema** — análise de hardware e reparo de software
- **Rede** — conectividade e configurações de interface
- **Processos** — visualização de tarefas e usuários logados
- **Diagnóstico** — testes automatizados com "nota de saúde" do PC

---

### v2 — Primeira GUI
- **Arquivo:** `tec-suporte-v2.py` / `dist/tec-suporte-v2.exe`
- Interface gráfica com **CustomTkinter**
- Monitoramento de CPU e RAM em tempo real
- Execução assíncrona com **threads** — interface nunca trava
- Log dinâmico com status de cada operação em tempo real
- Seletor de temas: Dark, Light e System

---

### v3 — Versão Atual ✨
- **Arquivo:** `tec-suporte-v4.py`
- Reescrita completa da arquitetura de interface
- Sidebar com **menus dropdown por clique** (sem flash preto — solução para limitação do `CTkToplevel` no Windows)
- **4 temas visuais:** Dark, Light, Azul, Verde — com troca em tempo real sem reiniciar
- Card de REDE exibindo **ONLINE/OFFLINE + latência** atualizado a cada 10s em background
- Diagnóstico de SSID Wi-Fi com **encoding adaptativo** (CP1252 → CP850 → UTF-8)
- Log colorizado por nível: `✔ OK` / `⚠ WARN` / `✖ ERRO` / `› CMD`
- Barra de progresso indeterminada durante operações longas
- Todos os processos em background — a UI **nunca trava**

---

## ⚙️ Funcionalidades (v4)

| Grupo | Funcionalidades |
|---|---|
| 🌐 **Rede** | Status de conexão (SSID, tipo, IP, latência, DNS), redes Wi-Fi salvas, flush DNS, renovar IP, sincronizar NTP, traceroute, diagnóstico completo |
| 💻 **Sistema** | Limpar temporários, limpeza avançada, SFC scan, DISM RestoreHealth, informações de hardware, GPUpdate |
| 🖨️ **Impressão** | Reset do Spooler, fila de impressão, gerenciar impressoras, reinstalar driver |
| 👤 **Usuários** | Desbloquear conta, alterar senha, logoff forçado, adicionar ao grupo Admin, listar usuários |
| ⚙️ **Serviços** | Top 5 processos por CPU, top 5 por RAM, gerenciador de serviços, Event Viewer, eventos críticos (últimas 24h) |
| 🔬 **Diagnóstico** | Saúde do sistema (score 0–100), verificar drivers, teste de memória, SMART de disco, tempo de boot |
| 🛠️ **Ferramentas** | Painel de Controle, Gerenciador de Tarefas, Editor do Registro, gerar relatório de hardware, exportar log |
| 🔑 **Ativação** | Windows e Office via Microsoft Activation Scripts (MAS) |

---

## 📊 Monitoramento em Tempo Real

O painel superior exibe 4 cards atualizados a cada segundo:

| Card | O que mostra |
|---|---|
| 🔄 CPU | Percentual de uso — verde / amarelo / vermelho |
| 🧠 RAM | Percentual de uso — verde / amarelo / vermelho |
| 💾 Disco | Percentual de uso — verde / amarelo / vermelho |
| 🌐 Rede | ONLINE + latência (ms) ou OFFLINE |

---

## 🚀 Como Executar

### Pré-requisitos

- Windows 10 ou 11
- Python 3.10+ (para rodar o `.py`)
- Ou use diretamente o `.exe` na pasta `dist/`

### Via Python

```bash
# Instalar dependências
pip install customtkinter psutil

# Executar (necessário privilégio de Administrador)
python tec-suporte-v4.py
```

> O script solicita elevação automática de privilégios via UAC caso não seja iniciado como Administrador.

### Via Executável

```
dist/tec-suporte-v4.exe
```

Clique com botão direito → **Executar como Administrador** para garantir acesso a todas as funcionalidades.

---

## 🧱 Tecnologias Utilizadas

| Tecnologia | Uso |
|---|---|
| `Python 3.x` | Linguagem base |
| `CustomTkinter` | Interface gráfica moderna |
| `psutil` | Monitoramento de CPU, RAM, disco e rede |
| `subprocess` | Execução de comandos do sistema |
| `threading` | Execução assíncrona sem travar a UI |
| `PowerShell` | Consultas WMI, leitura de perfis Wi-Fi com encoding correto |
| `PyInstaller` | Geração dos executáveis `.exe` |

---

## 📁 Estrutura do Repositório

```
tec-suporte/
├── dist/
│   ├── tec-suporte-v1.exe
│   ├── tec-suporte-v2.exe
│   └── tec-suporte-v3.exe
├── build/
├── tec-suporte-v1.py
├── tec-suporte-v1.spec
├── tec-suporte-v2.py
├── tec-suporte-v2.spec
├── tec-suporte-v3.py         ← versão atual
├── tec-suporte-v3.spec
└── README.md
```

---

## ⚠️ Observações

- **Administrador obrigatório:** a maioria dos comandos (SFC, DISM, net user, spooler, etc.) exige privilégios elevados. O programa solicita automaticamente via UAC.
- **Logs:** toda operação é registrada no painel com timestamp e nível. É possível exportar o log para `.txt` com um clique.
- **Relatórios:** a opção "Gerar Relatório" cria um arquivo `.txt` com `systeminfo` completo do hardware para auditoria.
- **Encoding:** o projeto lida com o encoding do console do Windows (CP1252/CP850) de forma adaptativa para garantir que nomes de redes Wi-Fi com acentos sejam exibidos corretamente.

---

## 📄 Licença

Este projeto é de código aberto. Sinta-se livre para usar, modificar e contribuir.

---