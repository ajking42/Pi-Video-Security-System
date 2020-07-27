

from detector import Detector
from flask_server import Flask_Server
from multiprocessing import Process, Queue




if __name__ == '__main__':
    
    # Initialise Queues to allow communication between processes
    # (not currently in use)
    detector_q = Queue()
    flask_q = Queue()

    #Initialise detector and server
    detector = Detector(detector_q, flask_q)
    server = Flask_Server()

    
    #Run server on separate process
    flask_process = Process(target=server.start, args=(detector_q, flask_q))
    flask_process.daemon = True
    flask_process.start()
    
    #Start detector
    detector.detect()
    flask_process.join()

