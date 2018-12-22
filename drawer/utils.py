import numpy as np
import cv2
from color_detection.detect_colors import get_hsv_range

def init_black_board():
    return cv2.flip(np.zeros((750, 650, 3),np.uint8),1)

def draw_shape(x, y, frame):
    cv2.circle(frame,(x,y),4,(255,255,255),7)

def erase_shape(x, y, frame):
    cv2.circle(frame, (x, y), 7, (0, 0, 0),12)


def color_colision(x1, y1, x2, y2, colision_distance=100):
    if abs(x1-x2) <= colision_distance and abs(y1-y2) <= colision_distance:
        return True
    else:
        return False

def get_point_color(frame, width, height):
    return get_hsv_range(frame[width][height])