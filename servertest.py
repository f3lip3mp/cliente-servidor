import subprocess
import platform
from socket import *
from datetime import datetime
import csv
import os
import time

# ip e porta
myHost = 'localhost'
myPort = 50001
url = ''
cmd = 'ping ' + url
sistema_operacional = platform.system()
diretorio = (os.getcwd())
diretorio1 = diretorio.split('\\')

def execute_cmd(cmd):
    print("------> CALL < -----")
    print(".... imprimindo na tela resultado da execucao ...")
    try:
        rc = subprocess.call(cmd, shell=True)
        print("Codigo retorno call: ", rc)
        return rc
    except:
        print('PING NÃO EXECUTADO.')
        msgsendall = "Servidor diz: Ping não realizado - Falhou"
        connection.sendall(msgsendall.encode("utf-8"))

socketServer = socket(AF_INET, SOCK_STREAM)

# bind da conexao
socketServer.bind((myHost, myPort))

def write_to_csv(responses):
    # Abre o arquivo CSV em modo de gravação
    with open('informacoes.csv', 'w', newline='') as file:
        writer = csv.writer(file)

        # Escreve o cabeçalho no arquivo CSV
        table_header = ["URL", "IP", "Status", "Data e Hora"]
        writer.writerow(table_header)

        # Escreve os dados de cada URL no arquivo CSV
        for domain, response in responses.items():
            ip = response["ip"]
            status = response["status"]
            date_time = response["date_time"]
            writer.writerow([domain, ip, status, date_time])

# Dados de login e senha
login = "admin"
senha = "123456"

while True:
    # servidor na escuta
    socketServer.listen(1)
    print("Servidor na escuta ...")

    connection, address = socketServer.accept()
    print("Conexao com: ", connection.getsockname())
    print("Servidor diz: Aceitei a conexao!")
    print("------ Comunicação entre Cliente e Servidor: Em andamento --------")
    # Autenticação do cliente
    autenticado = False
    while not autenticado:
        # Envia mensagem de login solicitando usuário e senha
        msgLogin = "Servidor diz: Entre com seu login e senha."
        connection.sendall(msgLogin.encode("utf-8"))

        # Recebe login e senha do cliente
        loginSenha = connection.recv(1024).decode("utf-8")
        loginCliente, senhaCliente = loginSenha.split("|")

        # Verifica se o login e senha são válidos
        if loginCliente == login and senhaCliente == senha:
            autenticado = True
            msgAutenticado = "Servidor diz: Autenticado com sucesso!"
            connection.sendall(msgAutenticado.encode("utf-8"))
        else:
            msgNaoAutenticado = "Servidor diz: Login e/ou senha inválidos. Tente novamente."
            connection.sendall(msgNaoAutenticado.encode("utf-8"))

    responses = {}  # Dicionário para armazenar as informações de cada URL

    while True:
        msgRcv = connection.recv(1024).decode('utf-8').upper()
        menu = '--- MENU ----' + '\n' + '[I]nformações' + '\n' + '[P]ing' + '\n' + '[D]iretório Atual' + '\n' + '[G]ravar em um diretório' + '\n' '[S]air' 
        connection.sendall(menu.encode("utf-8"))
        msgRcv = connection.recv(1024).decode('utf-8').upper()
        if msgRcv == 'S':
            print("\nEncerrando...")
            time.sleep(2)
            break
        elif msgRcv == 'P':
            connection.sendall('Digite a URL que você deseja consultar: '.encode('utf-8'))
            url = connection.recv(1024).decode('utf-8')
            cmd = "ping -n 2 " + url.lower()
            retorno = execute_cmd(cmd)
            # Enviar resposta para o cliente### depois de receber, envia resposta
            if retorno == 0:
                msgsendall = ("Servidor diz: Ping realizado com sucesso!\n")
                connection.sendall(msgsendall.encode("utf-8"))
            else:
                msgsendall = ("Servidor diz: Ping não realizado!\n"
                        "Não foi encontrado.")
                connection.sendall(msgsendall.encode("utf-8"))
            
            # Obter endereço IP dinamicamente
            try:
                ip = gethostbyname(url)
            except gaierror:
                ip = 'Endereço IP não encontrado'

            # Obter informações adicionais
            status = "Online" if retorno == 0 else "Offline"
            date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Adicionar as informações ao dicionário de respostas
            responses[url] = {
                "ip": ip,
                "status": status,
                "date_time": date_time
            }

            # Gravar as informações no arquivo CSV
            write_to_csv(responses)

        elif msgRcv == 'I':
            print('\n---------')
            with open('informacoes.csv', 'r') as f:
                info = f.read()
                connection.sendall(info.encode('utf-8'))
        elif msgRcv == 'D':
            if sistema_operacional == 'Windows':
                # Executar o comando para listar arquivos e diretórios
                resultado = subprocess.run('dir /B', shell=True, capture_output=True, text=True).stdout
                # Enviar o resultado para o cliente
                connection.sendall(resultado.encode('utf-8'))
            elif sistema_operacional == 'Linux':
                # Executar o comando para listar arquivos e diretórios
                resultado = subprocess.run('ls -1', shell=True, capture_output=True, text=True).stdout
                # Enviar o resultado para o cliente
                connection.sendall(resultado.encode('utf-8'))
            else:
                # Código para outros sistemas operacionais
                osUns = "Sistema operacional não reconhecido"
                connection.sendall(osUns.encode('utf-8'))
        elif msgRcv == 'G':

            diretorio = f'C:\\Users\\{diretorio1[2]}\\Desktop\\'
            diretorio2 = f'dir /B "{diretorio}"'
            processo = subprocess.run(diretorio2, shell=True, capture_output=True, text=True).stdout
            connection.sendall(processo.encode('utf-8'))
            time.sleep(0.1)
            respostaDir = connection.recv(1024).decode('utf-8')
            # caminho completo para o diretório de destino
            destino = os.path.join(diretorio, respostaDir)
            
            # Verifica se o diretório existe
            if os.path.exists(destino):
                # Verifica se é um diretório
                if os.path.isdir(destino):
                    subprocess.run(f'copy informacoes.csv "{destino}"', shell=True, capture_output=True, text=True).stdout
                    connection.sendall(f'Arquivo salvo na pasta {respostaDir}'.encode('utf-8'))
                else:
                    connection.sendall("O caminho especificado não é um diretório válido.".encode('utf-8'))
            else:
                connection.sendall("O diretório não existe.".encode('utf-8'))

        else:
            msgIncorreta = "Comando não é válido" 
            connection.sendall(msgIncorreta.encode('utf-8'))       
    break
socketServer.close()

