from detector import Detector
from multiprocessing import Process

#from flask_server import Flask_Server

if __name__ == '__main__':
    detector = Detector()
    #server = Flask_Server()

    p = Process(target=detector.detect)
    p.start()

    if detector.potato==2:
        print('2 potatoes!')