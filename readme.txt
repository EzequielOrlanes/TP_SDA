# Trabalho SDA 2025.1: Controle de Robô com CoppeliaSim, OPC UA e TCP/IP

Alunos: Ezequiel Orlanes
        Emanuel Figueiredo 

Este projeto implementa um CLP para controlar um robô simulado no CoppeliaSim, usando OPC UA para dados de processo e TCP/IP para controle do operador.

## Visão Geral

CLP (Este Projeto): Conecta-se ao servidor OPC UA (leitura de juntas, envio de garra), atua como servidor TCP/IP para comandos do operador e registra tudo em 'historiador.txt'.
CoppeliaSim: Ambiente de simulação do robô.
Servidor OPC UA: Gerencia a troca de dados entre CLP, CoppeliaSim e outros clientes (ex: MES).
Cliente de Supervisão (Não fornecido): Aplicação externa que controla o CLP via TCP/IP.
Cliente MES (Não fornecido): Cliente OPC UA que lê dados do servidor para 'mes.txt'.

## Estrutura de Pastas

.
├── brigde.py           # Lógica de comunicação OPC UA e CoppeliaSim.
├── clp_main.py         # Arquivo principal do CLP (servidor TCP/IP e controle).
├── README.md           # Este arquivo.
├── historiador.txt     # Log de operações.
└── mes.txt             # Exemplo de dados para MES.

## Requisitos

- Python
- CoppeliaSim (com robô Franka e servidor OPC UA ativo).
Bibliotecas Python: opcua, coppeliasim-zmqremoteapi-client, numpy.
Instalação de Dependências Python:
- pip install opcua coppeliasim-zmqremoteapi-client numpy

## Como Rodar (Ordem de Inicialização)

Inicie o CoppeliaSim: Abra o simulador, carregue o cenário do robô e garanta que o servidor OPC UA está ativo.
Inicie o CLP: No terminal, navegue até a pasta do projeto e execute:
python clp_main.py
O CLP iniciará o servidor TCP/IP, a comunicação OPC UA e a simulação no CoppeliaSim.
Conecte o Cliente de Supervisão (Opcional): Use um cliente TCP/IP para conectar-se a localhost:12345. Envie comandos JSON: {"joint": <numero_da_junta>, "value": <valor_em_graus>}. O cliente receberá a posição da garra e timestamp.
Conecte o Cliente MES (Opcional): Um cliente OPC UA separado leria os dados do processo do servidor OPC UA.

## Operação

O CLP lê as juntas do OPC UA, lê a posição da garra do simulador e a escreve de volta no OPC UA.
Comandos do cliente de supervisão movem as juntas do robô.
Todas as operações são registradas em 'historiador.txt'.
Para parar o CLP, pressione Ctrl+C no terminal.

### Notas Adicionais
Verifique permissões de firewall para as portas 53530 (OPC UA) e 12345 (TCP/IP).
A lógica em 'brigde.py' pode ser ajustada para controle mais complexo.
A representação da garra no simulador deve corresponder à leitura em 'brigde.py'.