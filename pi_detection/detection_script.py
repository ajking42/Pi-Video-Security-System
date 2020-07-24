import numpy as np
import tflite_runtime.interpreter as tflite
import cv2
from imutils.video import VideoStream
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
import time


from picamera.array import PiRGBArray
from picamera import PiCamera

class Detector:
    def start(self, queue1, queue2):
        queue1.put('message from detector!')
        # Path to frozen detection graph. This is the actual model that is used for the object detection.
        MODEL_NAME = 'ssd_mobilenet_v3_small_coco_2020_01_14'
        PATH_TO_CKPT = MODEL_NAME + '/model.tflite'

        # List of the strings that is used to add correct label for each box.
        PATH_TO_LABELS = 'mscoco_complete_label_map.pbtxt'

        # Define labels and categories from labelmap
        label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=90, use_display_name=True)
        category_index = label_map_util.create_category_index(categories)

        #Create a list of colour values for boxes
        colour_list = np.random.uniform(0, 255, size=(len(categories), 3))

        #Load a tflite model
        interpreter = tflite.Interpreter(PATH_TO_CKPT)
        interpreter.allocate_tensors()

        # Get input and output tensors.
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        # Find required image size for model input
        input_height = input_details[0]['shape'][1]
        input_width = input_details[0]['shape'][2]

        # Initialise the videostream 
        # vs = VideoStream().start()
        frame_rate_calc = 1
        freq = cv2.getTickFrequency()
        print('picam time')
        camera = PiCamera()

        camera.resolution = (input_width, input_height)
        rawCapture = PiRGBArray(camera, size=(input_width, input_height))
        print('Camera initilising')
        time.sleep(2)



        #while True:
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            t1 = cv2.getTickCount()
            
            # Get current frame
            frame = rawCapture.array
            
            (height, width) = frame.shape[:2]
            
            # Prepare frame for inference
            resized_frame = cv2.resize(frame, (input_width, input_height))
            image_np_expanded = np.expand_dims(resized_frame, axis=0)
            # Run inference
            interpreter.set_tensor(input_details[0]['index'], image_np_expanded)
            interpreter.invoke()
            
            # Retrieve output
            boxes = interpreter.get_tensor(output_details[0]['index'])[0]
            classes = interpreter.get_tensor(output_details[1]['index'])[0]
            scores = interpreter.get_tensor(output_details[2]['index'])[0]
            #Draw boxes and labels on frame   # Credit to pyimagesearch.com
            for i in range(0, len(classes)):
                if scores[i] > 0.6:
                    box = boxes[i]
                    (top, left, bottom, right) = (box * ([height, width, height, width])).astype('int')
                    prediction_index = classes[i].astype('int')
                    
                    label = "{}: {:.2f}%".format(categories[prediction_index]['name'], scores[i] * 100)
                    cv2.rectangle(frame, (left, top), (right, bottom), colour_list[prediction_index], 2)
                    cv2.putText(frame, label, (left, top-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, colour_list[prediction_index], 2)
                    queue1.put(label)
                    queue2.put(frame)


                    
            cv2.putText(frame,"FPS: {0:.2f}".format(frame_rate_calc),(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)

            cv2.imshow('frame', frame)
            t2 = cv2.getTickCount()
            t2 = (t2-t1)/freq
            
            

            frame_rate_calc = 1/t2

            rawCapture.truncate(0)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

