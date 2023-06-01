import cv2

from image_processing.angle_detection import AngleDetection, export_to_csv

class MeasureFromVideo:

    def __init__(self, video_file:str) -> None:
        '''
        Get the video informations.
        '''
        self.video_file = video_file
        self.signal = []
        
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
        angle_detection = AngleDetection()
        vidcap = cv2.VideoCapture(self.video_file)
        vidcap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        vidcap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.signal = [[None, round(f / fps, 3)] for f in range(frame_count)]
        self.state = True   # State of the video measuring
        
        success,image = vidcap.read()
        
        while success and self.state:
            edges = angle_detection.preprocess_image(image)
            angle_deg = angle_detection.detect_lines(image, edges)
            time_sec = round(count / fps, 3)
            self.signal[count] = [angle_deg, time_sec]
            count += 1
            success,image = vidcap.read()
        
        # Truncate the signal at the current time
        self.signal = self.signal[:count]
  
        vidcap.release()

        export_to_csv(self.signal, "mesure.csv")

        print("The signal was successfully saved")

def start_video_processing():
    # measure_from_video = MeasureFromVideo('data/videos_pendule/video_clean.mp4')
    measure_from_video = MeasureFromVideo('data/videos_pendule/video_robustness.avi')
    measure_from_video.run()

if __name__ == "__main__":
    start_video_processing()