import socket
import time
import tkinter as tk
from tkinter import ttk

class TCPClient:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.socket = None
        self.historian_file = "historiador.txt"
        
    def connect(self):
        """Conecta ao servidor TCP/IP"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"Conectado ao servidor {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return False
    
    def send_command(self, joint, value):
        """Envia comando para mover junta específica"""
        if not self.socket:
            print("Não conectado ao servidor")
            return None
        
        try:
            cmd = f"joint{joint}:{value}"
            self.socket.send(cmd.encode())
            
            # Recebe resposta
            response = self.socket.recv(1024).decode()
            
            # Processa resposta (formato: "OK/ERRO:mensagem|px,py,pz|timestamp")
            parts = response.split('|')
            status_msg = parts[0]
            position = parts[1] if len(parts) > 1 else "0,0,0"
            timestamp = parts[2] if len(parts) > 2 else time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Registra no historiador
            with open(self.historian_file, 'a') as f:
                f.write(f"{timestamp} - Junta {joint} = {value} - Posição: {position} - Status: {status_msg}\n")
            
            return {
                'status': status_msg,
                'position': position,
                'timestamp': timestamp
            }
        except Exception as e:
            print(f"Erro ao enviar comando: {e}")
            return None
    
    def close(self):
        """Fecha conexão"""
        if self.socket:
            self.socket.close()
            self.socket = None

class SupervisorGUI:
    def __init__(self, client):
        self.client = client
        self.root = tk.Tk()
        self.root.title("Supervisório do Robô")
        
        # Configuração da interface
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface gráfica"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Controle de junta
        ttk.Label(main_frame, text="Junta:").grid(row=0, column=0, sticky=tk.W)
        self.joint_var = tk.StringVar()
        self.joint_combobox = ttk.Combobox(main_frame, textvariable=self.joint_var, 
                                          values=[f"joint{i+1}" for i in range(7)])
        self.joint_combobox.grid(row=0, column=1, sticky=(tk.W, tk.E))
        self.joint_combobox.current(0)
        
        # Valor da junta
        ttk.Label(main_frame, text="Valor (-180 a 180):").grid(row=1, column=0, sticky=tk.W)
        self.value_var = tk.StringVar()
        self.value_entry = ttk.Entry(main_frame, textvariable=self.value_var)
        self.value_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        # Botão de envio
        self.send_button = ttk.Button(main_frame, text="Mover Junta", command=self.send_command)
        self.send_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Status
        self.status_var = tk.StringVar(value="Pronto")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=3, column=0, columnspan=2)
        
        # Posição da garra
        ttk.Label(main_frame, text="Posição da Garra:").grid(row=4, column=0, sticky=tk.W)
        self.position_var = tk.StringVar(value="0, 0, 0")
        ttk.Label(main_frame, textvariable=self.position_var).grid(row=4, column=1, sticky=tk.W)
        
        # Timestamp
        ttk.Label(main_frame, text="Última Atualização:").grid(row=5, column=0, sticky=tk.W)
        self.timestamp_var = tk.StringVar(value="N/A")
        ttk.Label(main_frame, textvariable=self.timestamp_var).grid(row=5, column=1, sticky=tk.W)
        
        # Ajusta tamanho das colunas
        main_frame.columnconfigure(1, weight=1)
        
    def send_command(self):
        """Envia comando para mover a junta"""
        try:
            joint = int(self.joint_var.get().replace("joint", ""))
            value = float(self.value_var.get())
            
            if not (-180 <= value <= 180):
                self.status_var.set("ERRO: Valor deve estar entre -180 e 180")
                return
            
            result = self.client.send_command(joint, value)
            
            if result:
                if result['status'].startswith("OK"):
                    self.status_var.set("Comando executado com sucesso")
                else:
                    self.status_var.set(result['status'])
                
                self.position_var.set(result['position'])
                self.timestamp_var.set(result['timestamp'])
        except ValueError:
            self.status_var.set("ERRO: Valor inválido")
    
    def run(self):
        """Executa a interface"""
        if self.client.connect():
            self.root.mainloop()
            self.client.close()
        else:
            print("Não foi possível conectar ao servidor")

if __name__ == "__main__":
    client = TCPClient()
    app = SupervisorGUI(client)
    app.run()