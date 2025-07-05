import time
import numpy as np
from opcua import Client
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
########################################################################
# Função para interpolação linear entre a posição atual e a posição alvo
########################################################################
def move_joint_smoothly(handle, target_position):

    # Tempo de movimento (em segundos)
    move_time = 1.0  # Ajuste o tempo de movimento desejado
    steps = 50  # Número de passos (quanto maior, mais suave será o movimento)
    delta_time = move_time / steps  # Intervalo de tempo entre os passos
    # Obtem a posição atual da junta
    current_position = sim.getJointPosition(handle)
    # Calcula o incremento necessário para mover a junta
    step_size = (target_position - current_position) / steps
    # Move a junta gradualmente
    for step in range(steps):
        new_position = current_position + step_size * (step + 1)
        sim.setJointTargetPosition(handle, new_position)
        time.sleep(delta_time)


########################################################################
# Inicia conexao com servidor OPCUA
########################################################################
def initOPC():
    # cria o client
    client = Client("opc.tcp://localhost:53530/OPCUA/SimulationServer")
    # conecta
    client.connect()
    # Obtém uma lista de servidores disponíveis na rede
    servers = client.find_servers()
    ##################
    # Imprime a lista de servidores encontrados
    for server in servers:
        print("-----------------------------")
        print("Server URI:", server.ApplicationUri)
        print("Server ProductURI:", server.ProductUri)
        print("Discovery URLs:", server.DiscoveryUrls)
        print("-----------------------------")

    # Pegando o nó de Objects
    root = client.get_objects_node()
    # Pegando o nó do robô
    robo = root.get_child(["3:Franka"])
    # Listando todos os filhos (nós)
    var = robo.get_children()
    juntas = var[:7]
    garra = var[-3:]

    print("Descobrindo juntas do robo dentro do robo:")
    for j in juntas:
        name = j.get_browse_name().Name
        value = j.get_value()
        print(f"{name} = {value}")

    print("Descobrindo juntas do robo dentro do robo:")
    for p in garra:
        name = p.get_browse_name().Name
        value = p.get_value()
        print(f"{name} = {value}")

    return juntas, garra


########################################################################
# Inicializa CoppeliaSim
########################################################################
def initCoppelia():
    # Conecta com o CoppeliaSim
    client = RemoteAPIClient()
    sim = client.getObject("sim")

    # Começa a simulação (certifique-se de que ela esteja pausada ou parada)
    sim.startSimulation()

    # Aguarda um pouco para garantir que tudo iniciou corretamente
    time.sleep(1)

    # Nomes das juntas do manipulador
    joint_names = [f"link{i+2}_resp" for i in range(6)]
    joint_handles = [
        sim.getObject("/Franka/" + name + "/joint") for name in joint_names
    ]

    return sim, joint_handles


########################################################################
# main
########################################################################
# inicializa cliente OPC
juntas, garra = initOPC()

# inicializa simulador
sim, joint_handles = initCoppelia()

# main loop
for _ in range(2000):

    # le todas as juntas do servidor
    for j in juntas:
        value = j.get_value()
    # Define uma posição alvo para as juntas (em radianos)
    target_positions = [
        np.clip(np.deg2rad(j.get_value()), -180.0, 180.0) for j in juntas
    ]  # Ajuste o número de juntas conforme necessário
    # Move as juntas suavemente para a posição alvo
    for h, pos in zip(joint_handles, target_positions):
        move_joint_smoothly(h, pos)
    position = sim.getObjectPosition(joint_handles[-1], -1)  # Referência: mundo
    # Espera um pouco para garantir que o movimento terminou
    time.sleep(0.1)
    # devolve a posição para o servidor
    for i, p in enumerate(garra):
        p.set_value(position[i])

# Para a simulação
sim.stopSimulation()
