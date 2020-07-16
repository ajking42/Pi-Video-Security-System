from detection_script import Detector
from multiprocessing import Queue

d = Detector()
d.start(Queue(), Queue())