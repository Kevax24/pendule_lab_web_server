import numpy as np
import cv2
import csv

class AngleDetection:

    def __init__(self) -> None:
        self.prev_angle = 0.0
        
    def preprocess_image(self, image):
        # Convert the image to the HSV format
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Select the saturation plane from the HSV image
        satur = hsv[:,:,1]

        # Blur the image with a bilateral filter to remove noise
        kernel_size = 9
        blur = cv2.bilateralFilter(satur,kernel_size,50,100)

        # Apply a canny edge detector to extract the edge from the image
        edges = cv2.Canny(blur,30,40,apertureSize = 3)

        return edges

    def detect_lines(self, image, edges, max_angle = 15, line_lenght = 120, angle_precision = 0.1):
        # Detect the lines woth the Hough transform
        lines = cv2.HoughLines(edges, 1, np.pi / 180 * angle_precision, line_lenght, None, 0, 0, -max_angle/180*np.pi, max_angle/180*np.pi)

        if lines is not None:
            # Select the line with the average angle on the left side of the pendulum
            lines = lines.reshape((len(lines), 2))
            rhos = lines[:,0]
            selected_lines = []
            threshold = 50
            
            # Select the line at the left
            min_rho = min(rhos)   # Pick the minimum rho
            left_rhos = rhos[:] < min_rho + threshold
            left_lines = lines[left_rhos]
            # Pick the median angle value
            thetas = left_lines[:,1]
            average = np.median(thetas)
            # Select the closest line to that angle
            idx = (np.abs(thetas - average)).argmin()
            selected_lines.append(left_lines[idx])
            
            # Select the line at the right
            min_rho = max(rhos)   # Pick the maximum rho
            right_rhos = rhos[:] > min_rho - threshold
            right_lines = lines[right_rhos]
            # Pick the median angle value
            thetas = right_lines[:,1]
            average = np.median(thetas)
            # Select the closest line to that angle
            idx = (np.abs(thetas - average)).argmin()
            selected_lines.append(right_lines[idx])
    
            # Take the average of the two angles, convert the angle to degrees
            angle_deg = sum([i[1] for i in selected_lines]) / len(selected_lines) * 180/np.pi
            # Round the angle for simplier exportation
            angle_deg = round(angle_deg, 2)
            self.prev_angle = angle_deg

        else:
            angle_deg = self.prev_angle
        
        return angle_deg
        

def export_to_csv(data:list, filename:str, header=['amplitude', 'time']) -> None:
    '''
    Export the data to a csv file
    '''
    with open(filename, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write multiple rows
        writer.writerows(data)
        