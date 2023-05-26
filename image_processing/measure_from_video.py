import cv2

from image_processing.angle_detection import AngleDetection, export_to_csv

class MeasureFromVideo:

    def __init__(self, video_file:str) -> None:
        '''
        Get the video informations.
        '''
        self.video_file = video_file
        
    def early_stopping(self):
        '''
        This function can be called to stop the acquisition earlier.
        '''
        self.state = False
        
    def run(self):
        '''
        This function read every image of the video and detect the angle of the pendulum.
        '''
        count = 0
        self.signal = []
        angle_detection = AngleDetection()
        vidcap = cv2.VideoCapture(self.video_file)
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        self.state = True   # State of the video measuring
        
        success,image = vidcap.read()
        
        while success and self.state:
            edges = angle_detection.preprocess_image(image)
            angle_deg = angle_detection.detect_lines(image, edges)
            time_sec = round(count / fps, 3)
            self.signal.append([angle_deg, time_sec])
            count += 1
            success,image = vidcap.read()
  
        vidcap.release()

        export_to_csv(self.signal, "mesure.csv")

        print("The signal was successfully saved")

def start_video_processing():
    # measure_from_video = MeasureFromVideo('Data/Videos_pendule/video_clean.mp4')
    measure_from_video = MeasureFromVideo('Data/Videos_pendule/video_robustness.avi')
    measure_from_video.run()

if __name__ == "__main__":
    start_video_processing()