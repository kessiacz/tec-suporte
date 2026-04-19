# Tec-Suporte: Automação para Suporte Técnico no Windows

Script desenvolvido em Python para automatizar tarefas comuns de suporte técnico, manutenção de sistema, reparo de arquivos do Windows etc.

## Versões do Projeto
O projeto está dividido em duas etapas de desenvolvimento:

### v1: Versão CLI (Linha de Comando)
- Arquivos: `tec-suporte-v1.py` e `tec-suporte-v1.exe` (na pasta dist)
- Interface: Terminal interativo (CLI).
- Foco: Execução leve, direta e baseada em menus numéricos.

### v2: Versão GUI (Interface Gráfica)
- Arquivos: `tec-suporte-v2.py` e `tec-suporte-v2.exe` (na pasta dist)
- Interface: Desenvolvida com a biblioteca `CustomTkinter`.
- Monitoramento: Indicadores de uso de CPU, RAM e Logs em tempo real.
- Execução Assíncrona: Uso de Threads para garantir que a interface permaneça responsiva durante manutenções longas.
- Log Dinâmico: Visualização em tempo real do status de cada operação e resposta dos comandos.
- Seletor de Temas: Alternância entre modos Dark, Light e System.

## Funcionalidades Principais
1.  Manutenção e Limpeza: Eliminação de arquivos temporários do usuário e do sistema, além de limpeza profunda via `cleanmgr`.
2.  Gestão de Rede: Flush de DNS, renovação de IP (Release/Renew), diagnóstico de portas e sincronização de horário com servidores NTP brasileiros.
3.  Reparo de Sistema: Com o SFC (System File Checker), DISM e CHKDSK.
4.  Gestão de Usuários: Interface facilitada para desbloqueio de contas e alteração de senhas.
5.  Impressão: Reinicialização rápida do Spooler de impressão e atalhos para fila de documentos.
6.  Relatórios: Geração automática de logs e relatórios detalhados de hardware e rede para auditoria.

### REQUISITOS:
- Sistema Operacional: Windows 10 ou 11.
- Python: 3.x instalado (caso rode o `tec-suporte.py`).
OBS: O script solicitará automaticamente permissões de Administrador, necessárias para a execução da maioria dos comandos de sistema.

### Arquivo Executável (tec-suporte.exe)
Clique no arquivo `tec-suporte.exe`, dentro da pasta dist (`dist/tec-suporte.exe`)

## Estrutura de Menus (versão 1)
- Manutenção: Focado em limpeza e otimização rápida.
- Sistema: Ferramentas de análise de hardware e reparo de software.
- Rede: Tudo relacionado a conectividade e configurações de interface.
- Processos: Visualização de tarefas e usuários logados.
- Diagnóstico: Testes automatizados que geram uma "nota de saúde" para o PC.

## Estrutura de Menus (versão 2)
- Rede: Focado em conectividade, DNS e tabelas IP.
- Sistema: Informações de hardware e ferramentas de reparo de imagem do Windows.
- Impressão: Soluções rápidas para travamentos de impressoras.
- Usuários: Administração de contas locais e permissões.
- Serviços: Visualização de processos pesados e monitor de eventos críticos.
- Ferramentas: Acesso rápido ao Painel de Controle e exportação de relatórios.

## Observações
- Logs: Toda operação bem-sucedida ou erro é registrado em um arquivo chamado log.txt na mesma pasta do programa.
- Relatórios: A opção "Gerar Relatório" cria um arquivo relatorio.txt contendo informações detalhadas do hardware e da rede para análise posterior.
- Segurança: O programa executa comandos que alteram configurações de rede e apagam arquivos temporários.
