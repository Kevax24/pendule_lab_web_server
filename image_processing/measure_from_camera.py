import cv2
import time

from image_processing.angle_detection import AngleDetection, export_to_csv

class MeasureFromCamera:

    def __init__(self, device_id=0) -> None:
        '''
        Get the camera informations.
        '''
        self.device_id = device_id
        self.signal = []
        
    def early_stopping(self):
        '''
        This function can be called to stop the acquisition earlier.
        '''
        self.state = False
        
    def run(self, measure_seconds=10):
        '''
        This function read every image of the video and detect the angle of the pendulum.
        '''
        count = 0
        self.state = True   # State of the video measuring
        self.signal = []
        angle_detection = AngleDetection()
        vidcap = cv2.VideoCapture(self.device_id, cv2.CAP_DSHOW)
        vidcap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        vidcap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        fps = 30
        vidcap.set(cv2.CAP_PROP_FPS, fps)
        self.signal = [[None, round(f / fps, 3)] for f in range(measure_seconds*fps)]
        
        # We need to check if camera
        # is opened previously or not
        if (vidcap.isOpened() == False): 
            print("Error reading video file")
        
        success,image = vidcap.read()
        
        start= time.time()
        last= time.time()
        while (last-start < measure_seconds) and success and self.state:
            edges = angle_detection.preprocess_image(image)
            angle_deg = angle_detection.detect_lines(image, edges)
            time_sec = round(last-start, 3)
            self.signal[count] = [angle_deg, time_sec]
            count += 1
            success,image = vidcap.read()
            last = time.time()
        
        # Truncate the signal at the current time
        self.signal = self.signal[:count]
  
        vidcap.release()

        export_to_csv(self.signal, "mesure.csv")

        print("The signal was successfully saved")

def start_video_processing(measure_seconds=10):
    measure_from_video = MeasureFromCamera(device_id=0)
    measure_from_video.run(measure_seconds)

if __name__ == "__main__":
    start_video_processing()