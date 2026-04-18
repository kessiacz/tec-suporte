# Tec-Suporte: Automação para Suporte Técnico no Windows

Script desenvolvido em Python para automatizar tarefas comuns de suporte técnico, manutenção de sistema, diagnóstico de rede e reparo de arquivos do Windows.

## Versões do Projeto
O projeto está dividido em duas etapas de desenvolvimento:

### v1: Versão CLI (Linha de Comando)
- Arquivos: `tec-suporte-v1.py` e `tec-suporte-v1.exe` (na pasta dist)
- Interface: Terminal clássico.
- Foco: Execução leve, direta e baseada em menus numéricos.

### v2: Versão GUI (Interface Gráfica)
- Arquivos: `tec-suporte-v2.py` e `tec-suporte-v2.exe` (na pasta dist)
- Interface: Desenvolvida em CustomTkinter.
- Dashboard de Monitoramento: Indicadores de uso de CPU, RAM e Logs em tempo real.
- Multi-threading: As ferramentas rodam em segundo plano, evitando que a interface trave durante processos longos.
- Log Integrado: Visualização do histórico de comandos diretamente na tela principal.
- Seletor de Temas: Alternância entre modos Dark, Light e System.

## Funcionalidades Principais
1. Manutenção: Limpeza de arquivos temporários e cache de DNS.
2. Gestão de Rede: Reset completo de stack TCP/IP, renovação de IP, teste de conexão e visualização de perfis Wi-Fi.
3. Diagnóstico de Sistema: Verificação de integridade de arquivos (SFC), reparo de imagem do Windows (DISM) e verificação de disco (CHKDSK).
4. Relatórios e Logs: Geração de relatórios completos do sistema e logs de execução das tarefas.
5. Monitoramento: Visualização de processos ativos, portas abertas e status de driver

### REQUISITOS:
- Sistema Operacional: Windows 10 ou 11.
- Python: 3.x instalado (caso rode o `tec-suporte.py`).
OBS: O script solicitará automaticamente permissões de Administrador, necessárias para a execução da maioria dos comandos de sistema.

### Arquivo Executável (tec-suporte.exe)
Clique no arquivo `tec-suporte.exe`, dentro da pasta dist (`dist/tec-suporte.exe`)

## Estrutura de Menus
- Manutenção: Focado em limpeza e otimização rápida.
- Sistema: Ferramentas de análise de hardware e reparo de software.
- Rede: Tudo relacionado a conectividade e configurações de interface.
- Processos: Visualização de tarefas e usuários logados.
- Diagnóstico: Testes automatizados que geram uma "nota de saúde" para o PC.

## Observações
- Logs: Toda operação bem-sucedida ou erro é registrado em um arquivo chamado log.txt na mesma pasta do programa.
- Relatórios: A opção "Gerar Relatório" cria um arquivo relatorio.txt contendo informações detalhadas do hardware e da rede para análise posterior.
- Segurança: O programa executa comandos que alteram configurações de rede e apagam arquivos temporários.
