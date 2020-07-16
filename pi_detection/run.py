from detection_script import Detector
from flask_server import Flask_Server
from multiprocessing import Process, Queue




if __name__ == '__main__':
    detector = Detector()
    server = Flask_Server()

    detector_q = Queue()
    flask_q = Queue()

    

    flask_process = Process(target=server.start, args=(detector_q, flask_q))
    flask_process.daemon = True
    flask_process.start()
    

    detector.start(detector_q, flask_q)
    flask_process.join()

