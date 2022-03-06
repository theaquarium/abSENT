import os
import sys
import signal
import threading
import time
from dev_env.webserver import start_webserver
from main import main

if __name__ == '__main__':
    print('Starting dev environment...')
    os.environ['absent_environment'] = 'dev'

    print('Starting threads...')

    ws_thread = threading.Thread(target=start_webserver, daemon=True)
    main_thread = threading.Thread(target=main, daemon=True)

    ws_thread.start()
    main_thread.start()

    main_thread.join()
