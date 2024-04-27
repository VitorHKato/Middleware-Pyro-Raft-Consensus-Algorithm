# Implementação do algoritmo de consenso Raft usando comunicação via Pyro5
# pyro5-ns [nome_host]     # Inicia o servidor de nomes (só existe um no network)
# Executar servidor e cliente
# pyro5-nsc list
# Executar servidor como python greeting-server.py [nome] [porta]

import Pyro5.api
import Pyro5.server
import random
import threading
from util import *


@Pyro5.api.expose                   # Permite o acesso remoto
class Peer:
    def __init__(self, name, port):
        self.name = str(name)
        self.port = int(port)
        self.daemon = Pyro5.api.Daemon(port=self.port)       # Cria o servidor que faz a ponte de comunicação
        self.state = states['follower']
        self.election_timer = random.uniform(1.5, 3)
        self.votes = 0
        self.voted = False
        self.leader = None

    def get_name(self):
        return self.name

    def get_voted(self):
        return self.voted

    def get_votes(self):
        return self.votes

    def get_state(self):
        return self.state

    def get_leader(self):
        return self.leader

    def set_votes(self, votes):
        self.votes = votes

    def set_voted(self, voted):
        self.voted = voted

    def set_state(self, state):
        self.state = states[state]

    def set_leader(self, leader):
        self.leader = leader

    def loop_daemon(self):
        print(f"{self.name} is running.")

        t = threading.Thread(target=self.daemon.requestLoop)
        t.start()

        self.election()

    def election(self):
        print(f"{self.name} time: {self.election_timer}")

        print(f"New leader: {self.leader}")

        if countdown_timer(self.election_timer) and not self.leader:
            print(f"Time's up {self.name}!")
            self.state = states['candidate']
            self.comunication()

            print(f'{self.name} after communcation: {self.state}, {self.votes}, {self.voted}')

            self.choose_leader()

        self.election()

    def comunication(self):
        if self.port != 9091:
            p = Pyro5.api.Proxy(uris['peer1'])
            if not p.get_voted() and p.get_state() == 'follower':
                p.vote(self.name)
                self.votes += 1
        if self.port != 9092:
            p = Pyro5.api.Proxy(uris['peer2'])
            if not p.get_voted() and p.get_state() == 'follower':
                p.vote(self.name)
                self.votes += 1
        if self.port != 9093:
            p = Pyro5.api.Proxy(uris['peer3'])
            if not p.get_voted() and p.get_state() == 'follower':
                p.vote(self.name)
                self.votes += 1
        if self.port != 9094:
            p = Pyro5.api.Proxy(uris['peer4'])
            if not p.get_voted() and p.get_state() == 'follower':
                p.vote(self.name)
                self.votes += 1

    def vote(self, name):
        self.voted = True
        self.election_timer = random.uniform(1.5, 3)
        print(f'new {self.name} time: {self.election_timer}')
        return "Vote received by {0} to {1}\n".format(self.name, name)

    def choose_leader(self):
        max_votes = 0
        leader = None

        p1 = Pyro5.api.Proxy(uris['peer1'])
        p2 = Pyro5.api.Proxy(uris['peer2'])
        p3 = Pyro5.api.Proxy(uris['peer3'])
        p4 = Pyro5.api.Proxy(uris['peer4'])

        if p1.get_votes() > max_votes:
            max_votes = p1.get_votes()
            leader = p1
        if p2.get_votes() > max_votes:
            max_votes = p2.get_votes()
            leader = p2
        if p3.get_votes() > max_votes:
            max_votes = p3.get_votes()
            leader = p3
        if p4.get_votes() > max_votes:
            leader = p4

        def reset(peer, state, leader):
            peer.set_voted(False)
            peer.set_votes(0)
            peer.set_state(state)
            peer.set_leader(leader.get_name())

        if leader:
            reset(p1, 'follower', leader)
            reset(p2, 'follower', leader)
            reset(p3, 'follower', leader)
            reset(p4, 'follower', leader)
            reset(leader, 'leader', leader)


def start_server(name, port):
    p = Peer(str(name), int(port))
    p.daemon.register(p, name)

    ns = Pyro5.api.locate_ns()
    ns.register(str(name), uris[name])

    # p1 = Pyro5.api.Proxy(uris['peer1'])
    # print(p1)

    p.loop_daemon()

# p2 = Peer('peer2', 9092)
# p3 = Peer('peer3', 9093)
# p4 = Peer('peer4', 9094)


# Fazer isso depois de a eleição estar pronta
# ns = Pyro5.api.locate_ns()  # Localiza o servidor de nomes
# ns.register(str(p1.name), uris['peer1'])  # Registra o nome (chave) e a uri do objeto
# ns.register(str(p2.name), uris['peer2'])  # Registra o nome (chave) e a uri do objeto


thread_a = threading.Thread(target=start_server, args=('peer1', 9091))
thread_b = threading.Thread(target=start_server, args=('peer2', 9092))
thread_c = threading.Thread(target=start_server, args=('peer3', 9093))
thread_d = threading.Thread(target=start_server, args=('peer4', 9094))

thread_a.start()
thread_b.start()
thread_c.start()
thread_d.start()

thread_a.join()
thread_b.join()
thread_c.join()
thread_d.join()




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


# Testar removendo um nó do daemon ?