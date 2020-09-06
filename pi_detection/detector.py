import numpy as np
import tflite_runtime.interpreter as tflite
import cv2
import os
import yaml
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
from queue import Queue
import time
from datetime import datetime        dir_path = f'{self.directory}detection_storage/'


class Detector:
    config = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)  

    
    

    def __init__(self, q1, q2):

       

        # Initialise Queues          
        self.queue1 = q1
        self.queue2 = q2
        
        print('Initialising detector')
        # Path to frozen detection graph. This is the actual model that is used for the object detection.
        MODEL_NAME = self.config['model_preference']
        print(F'Running model: {MODEL_NAME}')
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
        

    def detect(self, frame_count_bool):
        # Initialise the videostream 
        resolution = (self.input_width, self.input_height)
        print('Initilising PiCamera')
        camera = PiCamera()
        camera.resolution = resolution
        frame_rate_calc = 1
        freq = cv2.getTickFrequency()
        rawCapture = PiRGBArray(camera, size=resolution)
        time.sleep(2)
        print('Starting detection loop')
        frame_rate_list = []
        
        out = cv2.VideoWriter(f'video_storage/{datetime.now().strftime("%m-%d-%Y, %H:%M:%S")}.mp4',cv2.VideoWriter_fourcc('m','p','4','v'), 8, (self.input_width,self.input_height))
        avg_fps = 1
        frame_count = 1
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            t1 = cv2.getTickCount()
            # If user chooses to calculate video length by number of frames
            if frame_count >= 100 and frame_count_bool == False:
                self.saveVideo(out)
                print(frame_count)
                frame_count = 1
                avg_fps = sum(frame_rate_list)/len(frame_rate_list)
                print(avg_fps)
                frame_rate_list = []
                out = cv2.VideoWriter(f'video_storage/{datetime.now().strftime("%m-%d-%Y, %H:%M:%S")}.mp4',cv2.VideoWriter_fourcc('m','p','4','v'), avg_fps, (self.input_width,self.input_height))

            # If user wishes to calculate video length by approximated seconds 
            if frame_count >= avg_fps*30 and frame_count_bool == True:
                self.saveVideo(out)
                print(frame_count)
                frame_count = 1
                avg_fps = sum(frame_rate_list)/len(frame_rate_list)
                print(avg_fps)
                frame_rate_list = []
                out = cv2.VideoWriter(f'video_storage/{datetime.now().strftime("%m-%d-%Y, %H:%M:%S")}.mp4',cv2.VideoWriter_fourcc('H','E','V','C'), avg_fps, (self.input_width,self.input_height))

            
            
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
            #Draw boxes and labels on frame   # Credit to pyimagesearch.com
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
                    if(label_category in self.config['categories']):

                        # Include date and time of detection in file name
                        frame_time = datetime.now().strftime("%m-%d-%Y, %H:%M:%S")
                        frame_file_name = f'detection_storage/{frame_time} - {label}.png'

                        self.saveFrame(frame_file_name, frame)


                        # Put category into notification queue
                        self.queue2.put(label_category)
                        
            recorded_frame = frame.copy()
            # Adds fps to stream, but not to saved frames
            cv2.putText(frame,"FPS: {0:.2f}".format(frame_rate_calc),(10,self.input_height-10),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,0),1,cv2.LINE_AA)
            
            cv2.putText(recorded_frame, datetime.now().strftime("%m-%d-%Y, %H:%M:%S"),(10, self.input_height-10),cv2.FONT_HERSHEY_SIMPLEX,0.25,(255,255,0),1,cv2.LINE_AA)

            
            out.write(recorded_frame)
            #Show the frame - TODO: to be taken out in final implementation
            cv2.imshow('frame', recorded_frame)

            if self.queue1.full():
                self.queue1.get()
            self.queue1.put(frame)

            #Reset picamera
            rawCapture.truncate(0)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                out.release()
                break
           #Calculate fps
            t2 = cv2.getTickCount()
            t2 = (t2-t1)/freq
            frame_rate_calc = 1/t2

            frame_rate_list.append(frame_rate_calc)
            frame_count = frame_count + 1  

    
    def saveFrame(self, frame_file_name, detection_frame):
        dir_path = 'detection_storage/'

        detection_file_names = os.listdir(dir_path)

        # get file creation dates
        frames = ((os.path.getctime(f'{dir_path}{frame}'), frame) for frame in detection_file_names)

        sorted_detections = []
        
        # sort file names by creation date
        for date, frame in sorted(frames):
            sorted_detections.append(frame)
        
        # Get current size of detection folder
        folder_size = sum(os.path.getsize(f'{dir_path}{f}') for f in os.listdir(dir_path))
        
        # while folder is larger than specified size, delete oldest frames
        i = 0
        while(folder_size > self.config['max_imstorage']*1000):
            oldest_file = sorted_detections[i]
            i = i + 1
            os.remove(f'{dir_path}{oldest_file}')
            folder_size = sum(os.path.getsize(f'{dir_path}{f}') for f in os.listdir(dir_path))

        # write new frame to folder
        cv2.imwrite(frame_file_name, detection_frame)
        
    def saveVideo(self, VideoWriter):
        dir_path = 'video_storage/'

        video_file_names = os.listdir(dir_path)

        # get file creation dates
        files = ((os.path.getctime(f'{dir_path}{f}'), f) for f in video_file_names)

        sorted_files = []
        
        # sort file names by creation date
        for date, f in sorted(files):
            sorted_files.append(f)
        
        # Get current size of video folder
        folder_size = sum(os.path.getsize(f'{dir_path}{f}') for f in os.listdir(dir_path))
        
        # while folder is larger than specified size, delete oldest videos
        i = 0
        while(folder_size > self.config['max_vidstorage']*1000):
            oldest_file = sorted_files[i]
            i = i + 1
            os.remove(f'{dir_path}{oldest_file}')
            folder_size = sum(os.path.getsize(f'{dir_path}{f}') for f in os.listdir(dir_path))
        
        VideoWriter.release()


