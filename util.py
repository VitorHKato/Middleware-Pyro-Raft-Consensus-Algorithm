import time

states = {
    'follower': 'follower',
    'candidate': 'candidate',
    'leader': 'leader'
}

def countdown_timer(seconds, name):
    while seconds > 0:
        time.sleep(0.01)
        seconds -= 0.01
    print(f"Time's up {name}!")