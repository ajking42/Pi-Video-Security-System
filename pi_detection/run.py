#!/usr/bin/env python
from detector import Detector
from flask_server import Flask_Server
from multiprocessing import Process, Queue
import sys, os




if __name__ == '__main__':
    
    restart = True


    # Initialise Queues to allow communication between processes
    # (not currently in use)
    detector_q = Queue(maxsize=10)
    flask_q = Queue()

    #Initialise detector and server
    detector = Detector(detector_q, flask_q)
    server = Flask_Server()

    
    #Run server on separate process
    detection_process = Process(target=detector.detect, args=(False,))
    detection_process.daemon = True
    detection_process.start()

    # Notifier process to constantly check for new detections
    notifier = Process(target=server.notification, args=(flask_q,))
    notifier.daemon = True
    notifier.start()


    #Start detector
    server.start(detector_q, flask_q)
    print('Server terminated')

    detection_process.terminate()
    print('Detection process terminated')

    notifier.terminate()
    print('Notifier process terminated')

    if restart:
        print('Restarting system...')
        os.execv(sys.executable, ['python'] + sys.argv)





