import numpy as np
import tflite_runtime.interpreter as tflite
import cv2
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
from datetime import datetime

class Detector:
    desired_categories = ['person', 'dog', 'laptop','tv']
    

    def __init__(self, q1, q2):
        self.queue1 = q1
        self.queue2 = q2
        print('Initialising detector')
        # Path to frozen detection graph. This is the actual model that is used for the object detection.
        MODEL_NAME = 'ssd_mobilenet_v3_large_coco_2020_01_14'
        PATH_TO_CKPT = MODEL_NAME + '/model.tflite'

        # List of the strings that is used to add correct label for each box.
        PATH_TO_LABELS = 'mscoco_complete_label_map.pbtxt'

        # Define labels and categories from labelmap
        self.label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
        self.categories = label_map_util.convert_label_map_to_categories(self.label_map, max_num_classes=90, use_display_name=True)
        self.category_index = label_map_util.create_category_index(self.categories)

        #Create a list of colour values for boxes
        self.colour_list = np.random.uniform(0, 255, size=(len(self.categories), 3))

        #Load a tflite model
        self.interpreter = tflite.Interpreter(PATH_TO_CKPT)
        self.interpreter.allocate_tensors()

        # Get input and output tensors.
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        # Find required image size for model input
        self.input_height = self.input_details[0]['shape'][1]
        self.input_width = self.input_details[0]['shape'][2]

       
        print('Detector initilised')
        

    def detect(self): 
         # Initialise the videostream 
        print('Initilising PiCamera')
        camera = PiCamera()
        camera.resolution = (self.input_width, self.input_height)
        frame_rate_calc = 1
        freq = cv2.getTickFrequency()
        rawCapture = PiRGBArray(camera, size=(self.input_width, self.input_height))
        time.sleep(2)
        print('Starting detection loop')
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

            t1 = cv2.getTickCount()
            
            # Get current frame
            frame = rawCapture.array
            
            (height, width) = frame.shape[:2]
            
            # Prepare frame for inference
            resized_frame = cv2.resize(frame, (self.input_width, self.input_height))
            image_np_expanded = np.expand_dims(resized_frame, axis=0)
            # Run inference
            self.interpreter.set_tensor(self.input_details[0]['index'], image_np_expanded)
            self.interpreter.invoke()
            
            # Retrieve output
            boxes = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
            classes = self.interpreter.get_tensor(self.output_details[1]['index'])[0]
            scores = self.interpreter.get_tensor(self.output_details[2]['index'])[0]
            #Draw boxes and labels on frame   # Credit to pyimagesearch
            for i in range(0, len(classes)):
                if scores[i] > 0.6:
                    
                    box = boxes[i]
                    (top, left, bottom, right) = (box * ([height, width, height, width])).astype('int')
                    prediction_index = classes[i].astype('int')
                    
                    label_category = self.categories[prediction_index]['name']
                    label = "{}: {:.2f}%".format(label_category, scores[i] * 100)
                    cv2.rectangle(frame, (left, top), (right, bottom), self.colour_list[prediction_index], 2)
                    cv2.putText(frame, label, (left, top-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colour_list[prediction_index], 2)
                    
                    #Only save and send frames in list of desired categories
                    if(label_category in self.desired_categories):
                        frame_time = datetime.now().strftime("%m-%d-%Y, %H:%M:%S")
                        
                        detection = {
                        'time': frame_time,
                        'label': label,
                        }

                        frame_file_name = f'detection_storage/{frame_time} - {label}.png'
                        print(frame_file_name)

                        cv2.imwrite(frame_file_name, frame)

                        
                        self.queue1.put(label)
                        

            cv2.putText(frame,"FPS: {0:.2f}".format(frame_rate_calc),(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)

            cv2.imshow('frame', frame)
            t2 = cv2.getTickCount()
            t2 = (t2-t1)/freq
            frame_rate_calc = 1/t2

            rawCapture.truncate(0)
            
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

    def return_string():
        print('blah')            

