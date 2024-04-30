import time

states = {
    'follower': 'follower',
    'candidate': 'candidate',
    'leader': 'leader'
}

uris = {
    'peer1': 'PYRO:peer1@localhost:9091',
    'peer2': 'PYRO:peer2@localhost:9092',
    'peer3': 'PYRO:peer3@localhost:9093',
    'peer4': 'PYRO:peer4@localhost:9094',
}

HEARTBEAT_TIME = 2.25

def countdown_timer(seconds):
    while seconds > 0:
        time.sleep(0.01)
        seconds -= 0.01
    return True


