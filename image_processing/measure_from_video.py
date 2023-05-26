import cv2

from image_processing.angle_detection import AngleDetection, export_to_csv

class MeasureFromVideo:

    def __init__(self, video_file:str) -> None:
        '''
        Get the video informations.
        '''
        self.video_file = video_file
        self.count = 0
        self.signal = []
        
    def early_stopping(self):
        '''
        This function can be called to stop the acquisition earlier.
        '''
        self.state = False

        # Truncate the signal at the current time
        self.signal = self.signal[:self.count]
        
    def run(self):
        '''
        This function read every image of the video and detect the angle of the pendulum.
        '''
        self.count = 0
        angle_detection = AngleDetection()
        vidcap = cv2.VideoCapture(self.video_file)
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.signal = [[None, round(f / fps, 3)] for f in range(frame_count)]    # Initialize the signal with the good size
        self.state = True   # State of the video measuring
        
        success,image = vidcap.read()
        
        while success and self.state:
            edges = angle_detection.preprocess_image(image)
            angle_deg = angle_detection.detect_lines(image, edges)
            time_sec = round(self.count / fps, 3)
            self.signal[self.count] = [angle_deg, time_sec]
            self.count += 1
            success,image = vidcap.read()
  
        vidcap.release()

        export_to_csv(self.signal, "mesure.csv")

        print("The signal was successfully saved")

def start_video_processing():
    # measure_from_video = MeasureFromVideo('../Data/Videos_pendule/WIN_20230322_17_15_43_Pro.mp4')
    measure_from_video = MeasureFromVideo('../Data/Videos_pendule/filename1.avi')
    measure_from_video.run()

if __name__ == "__main__":
    start_video_processing()