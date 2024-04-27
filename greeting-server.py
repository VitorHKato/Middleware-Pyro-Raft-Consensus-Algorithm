# Implementação do algoritmo de consenso Raft usando comunicação via Pyro5
# pyro5-ns [nome_host]     # Inicia o servidor de nomes (só existe um no network)
# Executar servidor e cliente
# pyro5-nsc list
# Executar servidor como python greeting-server.py [nome] [porta]

import Pyro5.api
import Pyro5.server
import sys
import random
from util import *


@Pyro5.api.expose                   # Permite o acesso remoto
class Peer:
    def __init__(self):
        self.name = sys.argv[1]
        self.port = sys.argv[2]
        self.daemon = Pyro5.server.Daemon(port=int(self.port))  # Cria o servidor que faz a ponte de comunicação
        self.state = states['follower']
        self.election_timer = random.uniform(1.5, 3)

        self.election()
        self.comunication()

    def loop_daemon(self):
        print(f"{self.name} is running.\n")
        self.daemon.requestLoop()

    def get_message(self):
        return "Mensagem do {0}\n".format(self.name)

    def election(self):
        print(f"{self.name} time: {self.election_timer}")
        countdown_timer(self.election_timer, self.name)
        pass
        # Ver se antes de zerar o timer, recebi uma mensagem de algum par

    def comunication(self):
        if self.port == '9091':
            p1 = Pyro5.api.Proxy('PYRONAME:peer2')
            print(p1.get_message())


p = Peer()
uri = p.daemon.register(Peer)


# Fazer isso depois de a eleição estar pronta
ns = Pyro5.api.locate_ns()  # Localiza o servidor de nomes
ns.register(str(p.name), uri)  # Registra o nome (chave) e a uri do objeto

print(uri)

# print(p.daemon.uriFor('peer1'))  #PYRO:peer.one@localhost:9090

p.loop_daemon()




def electionTimeout():      # Retorna a uri do lider
    pass

# Eleição
# Criar 4 nós que iniciam como seguidores
# Se não receber msg do líder, se torna um candidato
# Candidato envia requisição de votos e as recebe dos demais
# Candidato vira líder se receber o maior numero de votos

    # Election timeout
    # Tempo random que um seguidor espera para virar um candidato (150ms - 300ms)
    # O primeiro que zerar o tempo, inicia uma nova eleição
    # O nó que receber uma requisição de eleição e não tiver votado ainda, vota para o primeiro candidato que o requisitou e reseta o tempo de requisição
    # Quem tiver o maior número de votos vira o líder
    # O líder envia "Append entries" para os demais, em intervalos específicos (HeartBeat Timeout)
    # Demais respondem de volta
    # Esse loop continua até que um seguidor pare de receber os append entries e se torna um candidato

    # Se tiverem 2 candidatos ao mesmo tempo, será feito uma nova eleição entre os 2 candidatos


# Replicação
# Qualquer alteração passa pelo líder agora e fica armazenada nele como log
# Depois ele replica essa informação para os demais
# Quando receber a confirmação de envio dos demais, ele "comita" o valor e replica para os demais "comitarem" tb

# Já eleito um líder, o cliente envia uma requisição para o líder e ele armazena a informação em um log, no próximo "Heartbeat" ele envia
# essa informação para os seguidores
# Depois essa informação é comitada e enviada para o cliente de volta

