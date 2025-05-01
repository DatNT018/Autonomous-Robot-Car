import cv2
import numpy as np
import math
import sys
import time
import RPi.GPIO as GPIO
import main_motor as mM
from picamera2 import Picamera2



picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (320, 240)}))
picam2.start()

mM.motor_init()



def detect_edges(frame):
    # filter for blue lane lines

    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    cv2.imshow("HSV",hsv)
    lower_blue = np.array([0, 70, 75], dtype = "uint8")    #[0, 150, 50]      [0, 70, 75]
    upper_blue = np.array([15, 191, 185], dtype="uint8")      #[10, 255, 255]     15, 191, 185]
    mask = cv2.inRange(hsv,lower_blue,upper_blue)
    

    cv2.imshow("mask",mask)
    
    # detect edges
    edges = cv2.Canny(mask, 200,400)  #50, 100
    cv2.imshow("edges",edges)
    
    return edges

def region_of_interest(edges):
    height = edges.shape[0]
    width = edges.shape[1]    
    mask = np.zeros_like(edges)

    # only focus lower half of the screen
    polygon = np.array([[
        (0, height),
        (0,  height//2),
        (width , height//2),
        (width , height),
    ]], np.int32)
    
    cv2.fillPoly(mask, polygon, 255)
    
    cropped_edges = cv2.bitwise_and(edges, mask)
    cv2.imshow("roi",cropped_edges)
    
    return cropped_edges
'''
    Arguments for HoughLinesP

    rho : Distance Precision
    The hough Line Transform algorithm represents line in polar coordinates -> origin (rho) and angle (theta)
    rho specifies distance resolution in pixels.
    rho of 1 means two lines that are very close to each other but differ by a singe pixel will be considered different lines

    theta : Angular Precision
    It defines angular precision of hough transform. Means precision with which algo detects lines at different angle
    It is defined in radians
    If theta is np.Pi / 180 , that gives precision of 1 degree

    min_threshold : Minimum number of votes required for line to be considered

    lines : np.array([]) Empty array to store detected line segments

    min_line_length : Minimum length of a line to be considered

    max_line_gap : Max gap in segment to be considered as same line
    '''
def detect_line_segments(cropped_edges):
    
    rho = 1  
    theta = np.pi / 180  
    min_threshold = 10  
    minLineLength=20       #5 
    maxLineGap= 4        #150
    
    line_segments = cv2.HoughLinesP(cropped_edges, rho, theta, min_threshold, 
                                    np.array([]), minLineLength, maxLineGap)

    return line_segments

def average_slope_intercept(frame, line_segments):
    lane_lines = []
    height = frame.shape[0]
    width = frame.shape[1]
    left_fit = []
    right_fit = []

    #No found lines
    if line_segments is None:
        print("no line segments detected")
        return lane_lines

    boundary = 1/3
    left_region_boundary = width * (1 - boundary)
    right_region_boundary = width * boundary
    
    for line_segment in line_segments:
        for x1, y1, x2, y2 in line_segment:
            # skip vertical lines as they have infinite slope
            if x1 == x2:
                print("skipping vertical lines (slope = infinity")
                continue

            fit = np.polyfit((x1, x2), (y1, y2), 1)
            # slope = coff[0]
            # intercept = coff[1]
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - (slope * x1)
            # note that y axis is inverted in matrix of images. 
            # so as x (width) increases, y(height) values decreases
            # this is reason why slope of right nane is positive and left name is negative

            
             # negative slop -> left lane marking  /
            #                                    /
            #                                   /
            #                                  /
            if slope < 0:
                if x1 < left_region_boundary and x2 < left_region_boundary:
                    left_fit.append((slope, intercept))

            # positive slop -> right lane marking  \
            #                                       \
            #                                        \
            #                                         \
            else:
                if x1 > right_region_boundary and x2 > right_region_boundary:
                    right_fit.append((slope, intercept))

    # averaging all the lines in each group to get a single line out of them
    # if got left lane, convert to point form from intercept form
    left_fit_average = np.average(left_fit, axis=0)
    if len(left_fit) > 0:
        lane_lines.append(make_points(frame, left_fit_average))

    right_fit_average = np.average(right_fit, axis=0)
    if len(right_fit) > 0:
        lane_lines.append(make_points(frame, right_fit_average))

    return lane_lines

# Create points from the lane lines with slop and intercept
def make_points(frame, line):
    height = frame.shape[0]
    width = frame.shape[1]
    slope = line[0]
    intercept = line[1]
    
    y1 = height  # bottom of the frame
    y2 = int(y1 / 2)  # make points from middle of the frame down
    
    if slope == 0:
        slope = 0.1
        
    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)
    
    return [[x1, y1, x2, y2]]

#drawm lines
                                                            #6
def display_lines(frame, lines, line_color=(0, 255, 0), line_width=2):
    line_image = np.zeros_like(frame)
    
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)

#cv2.addWeighted(image1, alpha, image2, beta, gamma) 
#output = alpha * image1 + beta * image2 + gamma
    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    cv2.imshow("lines", line_image)
    return line_image


def display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5 ):
    heading_image = np.zeros_like(frame)
    height = frame.shape[0]
    width = frame.shape[1]
    steering_angle_radian = steering_angle / 180.0 * math.pi
    
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
    y2 = int(height / 2)
    
    cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
    heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)
    
    return heading_image

def get_steering_angle(frame, lane_lines):
    
    height,width,_ = frame.shape
    
    if len(lane_lines) == 2:
        _, _, left_x2, _ = lane_lines[0][0]
        _, _, right_x2, _ = lane_lines[1][0]
        mid = int(width / 2)
        x_offset = (left_x2 + right_x2) / 2 - mid
        y_offset = int(height / 2)
        
    elif len(lane_lines) == 1:
        x1, _, x2, _ = lane_lines[0][0]
        x_offset = x2 - x1
        y_offset = int(height / 2)
        
    elif len(lane_lines) == 0:
        x_offset = 0
        y_offset = int(height / 2)
        
    angle_to_mid_radian = math.atan(x_offset / y_offset)
    angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)  
    steering_angle = angle_to_mid_deg + 90
    
    return steering_angle



time.sleep(5)

speed = 10
lastTime = 0
lastError = 0

kp = 0.4
kd = kp * 0.65

while True:
    frame = picam2.capture_array()
    #frame = cv2.flip(frame, -1)
    frame = cv2.GaussianBlur(frame, (5, 5), 0)
    
    
    edges = detect_edges(frame)
    roi = region_of_interest(edges)
    line_segments = detect_line_segments(roi)
    lane_lines = average_slope_intercept(frame,line_segments)
    lane_lines_image = display_lines(frame,lane_lines)
    steering_angle = get_steering_angle(frame, lane_lines)
    heading_image = display_heading_line(lane_lines_image,steering_angle)
    

    cv2.imshow("original", frame)
    cv2.imshow("heading line", heading_image)

    now = time.time()
    dt = now - lastTime

    deviation = steering_angle - 90
    error = abs(deviation)
    
    if deviation < 5 and deviation > -5:
        deviation = 0
        error = 0
        mM.stop()
        

    elif deviation > 5: # steer right if the deviation is positive
        mM.right()
        time.sleep(0.1)

    elif deviation < -5: # steer left if deviation is negative
        mM.left()
        time.sleep(0.1)

    derivative = kd * (error - lastError) / dt
    proportional = kp * error
    PD = int(speed + derivative + proportional)
    spd = abs(PD)

    if spd > 25:
        spd = 50
        
        
    mM.forward_with_speed(spd)
    time.sleep(0.3)

    lastError = error
    lastTime = time.time()
        

    key = cv2.waitKey(1)
    if key == 27:
        break
    


picam2.stop()
cv2.destroyAllWindows()
GPIO.cleanup()



