import time
from opcua import Client

class MESClient:
    def __init__(self, server_url):
        self.server_url = server_url
        self.client = None
        self.joints = []
        self.gripper = []
        self.running = False
        
    def connect(self):
        """Conecta ao servidor OPC UA"""
        try:
            self.client = Client(self.server_url)
            self.client.connect()
            
            # Obtém nós das juntas e garra
            root = self.client.get_objects_node()
            robo = root.get_child(["3:Franka"])
            var = robo.get_children()
            self.joints = var[:7]
            self.gripper = var[-3:]
            
            print("Conectado ao servidor OPC UA")
            return True
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return False
    
    def collect_data(self):
        """Coleta dados do robô e salva no arquivo"""
        while self.running:
            try:
                # Lê valores atuais
                joint_values = [j.get_value() for j in self.joints]
                gripper_position = [p.get_value() for p in self.gripper]
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                
                # Formata dados para salvar
                data_line = f"{timestamp} - Juntas: {joint_values} - Garra: {gripper_position}\n"
                
                # Salva no arquivo
                with open("mes.txt", "a") as f:
                    f.write(data_line)
                
                time.sleep(1)  # Coleta dados a cada 1 segundo
            except Exception as e:
                print(f"Erro ao coletar dados: {e}")
                time.sleep(5)
    
    def start(self):
        """Inicia o cliente MES"""
        if self.connect():
            self.running = True
            print("MES iniciado. Pressione Ctrl+C para parar.")
            
            try:
                self.collect_data()
            except KeyboardInterrupt:
                self.stop()
    
    def stop(self):
        """Para o cliente MES"""
        self.running = False
        if self.client:
            self.client.disconnect()
        print("MES parado.")

if __name__ == "__main__":
    mes = MESClient("opc.tcp://localhost:53530/OPCUA/SimulationServer")
    mes.start()