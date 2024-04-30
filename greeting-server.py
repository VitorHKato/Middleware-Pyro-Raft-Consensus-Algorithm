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
        self.heartbeated = False
        self.heartbeat_time = HEARTBEAT_TIME

        self.name_server = Pyro5.api.locate_ns()
        self.log_value = None
        self.value = None

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

    def get_heartbeated(self):
        return self.heartbeated

    def get_election_timer(self):
        return self.election_timer

    def get_log_value(self):
        return self.log_value

    def get_value(self):
        return self.value

    def get_name_server(self):
        return self.name_server

    def set_votes(self, votes):
        self.votes = votes

    def set_voted(self, voted):
        self.voted = voted

    def set_state(self, state):
        self.state = states[state]

    def set_leader(self, leader):
        self.leader = leader

    def set_heartbeated(self, heartbeated):
        self.heartbeated = heartbeated

    def set_election_timer(self, election_timer):
        self.election_timer = election_timer

    def set_value(self, value):
        self.value = value
        print(f'Set {self.get_name()} value: {value}')

    def set_log_value(self, log_value):
        self.log_value = log_value
        print(f'Set {self.get_name()} log value: {log_value}')

    def loop_daemon(self):
        print(f"{self.name} is running.")

        t = threading.Thread(target=self.daemon.requestLoop)
        t.start()

        self.election()

    def election(self):
        print(f"{self.name} time: {self.election_timer}")

        print(f"New leader: {self.leader}")

        self.voted = False

        if countdown_timer(self.heartbeat_time) and self.leader == self.name:
            self.append_entries()

        if countdown_timer(self.election_timer) and self.heartbeated is False and self.leader != self.name:

            if self.voted is False:
                print(f"Time's up {self.name}!")
                self.state = states['candidate']
                self.request_vote()

                self.choose_leader()

        # Reinicia o heartbeat
        self.heartbeated = False
        self.heartbeat_time = HEARTBEAT_TIME
        # self.leader = None

        self.election()

    def request_vote(self):
        # Vota a si mesmo
        self.vote(self.name)
        self.votes += 1

        print(f'{self.name} requested vote.')

        def vote(p):
            p.vote(self.name)
            self.votes += 1

        if self.port != 9091:
            p = Pyro5.api.Proxy(uris['peer1'])
            if not p.get_voted() and p.get_state() == 'follower':
                vote(p)
        if self.port != 9092:
            p = Pyro5.api.Proxy(uris['peer2'])
            if not p.get_voted() and p.get_state() == 'follower':
                vote(p)
        if self.port != 9093:
            p = Pyro5.api.Proxy(uris['peer3'])
            if not p.get_voted() and p.get_state() == 'follower':
                vote(p)
        if self.port != 9094:
            p = Pyro5.api.Proxy(uris['peer4'])
            if not p.get_voted() and p.get_state() == 'follower':
                vote(p)

    def vote(self, name):
        self.voted = True
        self.election_timer = random.uniform(1.5, 3)
        print(f'new {self.name} time: {self.election_timer}')
        return "Vote received by {0} to {1}\n".format(self.name, name)

    def append_entries(self):
        def set_values(p):
            p.set_heartbeated(True)
            p.set_election_timer(random.uniform(1.5, 3))
            print(f'New {p.get_name()} time after heartbeat: {p.get_election_timer()}')
            if self.log_value:
                p.set_log_value(self.log_value)
                self.set_value(p.get_log_value())
                self.log_value = None
            if self.value:
                p.set_value(self.value)
                p.set_log_value(None)

        if self.port != 9091:
            p = Pyro5.api.Proxy(uris['peer1'])
            if p.get_state() == 'follower':
                set_values(p)
        if self.port != 9092:
            p = Pyro5.api.Proxy(uris['peer2'])
            if p.get_state() == 'follower':
                set_values(p)
        if self.port != 9093:
            p = Pyro5.api.Proxy(uris['peer3'])
            if p.get_state() == 'follower':
                set_values(p)
        if self.port != 9094:
            p = Pyro5.api.Proxy(uris['peer4'])
            if p.get_state() == 'follower':
                set_values(p)

        print(f'{self.get_name()} log value: {self.get_log_value()}')
        print(f'{self.get_name()} value: {self.get_value()}')

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
            # peer.set_voted(False)
            peer.set_votes(0)
            peer.set_state(state)
            peer.set_leader(leader.get_name())

        if leader:
            # Remove o líder antigo do servidor de nomes
            if str(leader.get_name()) != str(leader.get_leader()) and leader.get_leader() is not None:
                leader.get_name_server().remove(leader.get_leader())

            reset(p1, 'follower', leader)
            reset(p2, 'follower', leader)
            reset(p3, 'follower', leader)
            reset(p4, 'follower', leader)
            reset(leader, 'leader', leader)

            leader.get_name_server().register(leader.get_name(), uris[leader.get_name()])

            print(f'New leader after vote: {leader.get_name()}')

        for name, uri in leader.get_name_server().list().items():
            print(f"Registered uri's in name server: {str(name)}: {str(uri)}")


def start_server(name, port):
    p = Peer(str(name), int(port))
    p.daemon.register(p, name)

    p.loop_daemon()

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
# Ver a questão de poder ocorrer novas eleições após selecionado um líder