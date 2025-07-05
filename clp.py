import threading
import socket
import time
from opcua import Client

class CLP:
    def __init__(self):
        # Configurações do OPC UA
        self.opcua_url = "opc.tcp://localhost:53530/OPCUA/SimulationServer"
        self.joints = []
        self.gripper = []
        
        # Configurações do servidor TCP/IP
        self.tcp_host = 'localhost'
        self.tcp_port = 5000
        self.server_socket = None
        self.running = False
        
        # Dados do robô
        self.joint_values = [0.0] * 7
        self.gripper_position = [0.0, 0.0, 0.0]
        
    def init_opcua(self):
        """Inicializa conexão com servidor OPC UA"""
        self.opcua_client = Client(self.opcua_url)
        self.opcua_client.connect()
        
        # Obtém nós das juntas e garra
        root = self.opcua_client.get_objects_node()
        robo = root.get_child(["3:Franka"])
        var = robo.get_children()
        self.joints = var[:7]
        self.gripper = var[-3:]
        
        print("Conexão OPC UA estabelecida com sucesso!")
    
    def opcua_thread(self):
        """Thread para comunicação com OPC UA"""
        while self.running:
            try:
                # Lê posição da garra
                for i, p in enumerate(self.gripper):
                    self.gripper_position[i] = p.get_value()
                
                # Atualiza posições das juntas
                for i, j in enumerate(self.joints):
                    self.joint_values[i] = j.get_value()
                
                time.sleep(0.1)
            except Exception as e:
                print(f"Erro OPC UA: {e}")
                time.sleep(1)
    
    def handle_client(self, conn, addr):
        """Lida com conexões de clientes TCP/IP"""
        print(f"Conexão estabelecida com {addr}")
        
        try:
            while self.running:
                # Recebe comando do cliente
                data = conn.recv(1024).decode()
                if not data:
                    break
                
                # Processa comando (formato: "joint:value")
                if ':' in data:
                    joint, value = data.split(':')
                    try:
                        joint_idx = int(joint.replace('joint', '')) - 1
                        value = float(value)
                        
                        if 0 <= joint_idx < 7 and -180 <= value <= 180:
                            # Envia comando para o robô
                            self.joints[joint_idx].set_value(value)
                            response = f"OK:joint{joint_idx+1} set to {value}"
                        else:
                            response = "ERRO:Valor inválido"
                    except (ValueError, IndexError):
                        response = "ERRO:Comando inválido"
                else:
                    response = "ERRO:Formato inválido"
                
                # Envia resposta com posição atual da garra
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                response += f"|{self.gripper_position[0]},{self.gripper_position[1]},{self.gripper_position[2]}|{timestamp}"
                conn.send(response.encode())
                
        except Exception as e:
            print(f"Erro na conexão com {addr}: {e}")
        finally:
            conn.close()
            print(f"Conexão com {addr} encerrada")
    
    def tcp_server_thread(self):
        """Thread para servidor TCP/IP"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.tcp_host, self.tcp_port))
        self.server_socket.listen(5)
        print(f"Servidor TCP/IP iniciado em {self.tcp_host}:{self.tcp_port}")
        
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr)).start()
            except Exception as e:
                print(f"Erro no servidor TCP: {e}")
    
    def start(self):
        """Inicia o CLP"""
        self.running = True
        
        # Inicia conexão OPC UA
        self.init_opcua()
        
        # Inicia threads
        threading.Thread(target=self.opcua_thread, daemon=True).start()
        threading.Thread(target=self.tcp_server_thread, daemon=True).start()
        
        print("CLP iniciado. Pressione Ctrl+C para parar.")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Para o CLP"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        if hasattr(self, 'opcua_client'):
            self.opcua_client.disconnect()
        print("CLP parado.")

if __name__ == "__main__":
    clp = CLP()
    clp.start()