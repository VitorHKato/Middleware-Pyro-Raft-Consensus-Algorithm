import Pyro5.api

peer_msg = Pyro5.api.Proxy('PYRONAME:peer3')                  # Proxy intercepta a chamada do objeto como se fosse ele mesmo
                                                              # Já localiza o servidor de nomes e consulta a URI passada
print(peer_msg.set_log_value(7))
