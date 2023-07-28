from socket import *
import time

# ip, porta
myHost = 'localhost'
myPort = 50001

# objeto socket - Cliente
socketClient = socket(AF_INET, SOCK_STREAM)

# cliente apto a pedir/solicitar conexão com servidor
print("Cliente solicitando conexão com o servidor...")
socketClient.connect((myHost, myPort))
print("Cliente diz: Servidor me aceitou :D")
print("------ Comunicação entre Cliente e Servidor: Em andamento --------")

autenticado = False
while not autenticado:
    # Recebe mensagem de login do servidor
    msgLogin = socketClient.recv(1024).decode("utf-8")
    print(msgLogin)

    # Envia login e senha para o servidor
    login = input("Login: ")
    senha = input("Senha: ")
    loginSenha = f"{login}|{senha}"
    socketClient.send(loginSenha.encode("utf-8"))

    # Recebe resposta de autenticação do servidor
    respostaAutenticacao = socketClient.recv(1024).decode("utf-8")
    print(respostaAutenticacao)

    if respostaAutenticacao == "Servidor diz: Autenticado com sucesso!":
        autenticado = True
        break

# Troca de mensagens
while True:
    
    msgrsp = input("Cliente diz: ").upper()
    if msgrsp.strip() == "":
        print("Valor inválido.")
        break
    else:
        socketClient.send(msgrsp.encode("utf-8"))
        menu = socketClient.recv(1024).decode("utf-8")
        print(f'\n--------\n{menu}\n--------\n')
        msgrsp = input("Cliente diz: ").upper()
        socketClient.send(msgrsp.encode("utf-8"))
    if msgrsp == 'S':
        print("Encerrando...")
        time.sleep(2)
        break

    msgrcv = socketClient.recv(1024).decode('utf-8')
    print(msgrcv)

socketClient.close()
