

from detector import Detector
from flask_server import Flask_Server
from multiprocessing import Process, Queue




if __name__ == '__main__':
    

    detector_q = Queue()
    flask_q = Queue()

    detector = Detector(detector_q, flask_q)
    server = Flask_Server()

    

    flask_process = Process(target=server.start, args=(detector_q, flask_q))
    flask_process.daemon = True
    flask_process.start()
    

    detector.detect()
    flask_process.join()

