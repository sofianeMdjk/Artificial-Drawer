import cv2
def color_ranges():
    cr = {}
    cr["blue"] = [(101,50,38), (110,255,255)]
    cr["red"] = [(160,20,70), (190,255,255)]
    cr["green"] = [(66, 122, 129), (97, 100, 117)]
    cr["brown"] = [(10,100,20), (20,255,200)]
    cr["yellow"] = [(23, 59, 119), (54, 255, 255)]
    cr["black"] = [(0,0,0),(10,10,10)]
    cr["orange"] = [(10,100,20), (25,255,255)]

    return cr


def check_color_range(color, lower, upper):
    low_r, low_g, low_b = lower
    upper_r, upper_g, upper_b = upper
    color_r, color_g, color_b = color

    check_lower = (color_r>=low_r)
    check_upper = (color_r<=upper_r)

    if check_lower and check_upper:
        return True
    else:
        return False


def get_lower_upper_range(color_point):
    ranges = color_ranges()
    for color, color_range in ranges.items():
        lower_range = color_range[0]
        upper_range = color_range[1]
        if check_color_range(color_point, lower_range, upper_range):
            return color, color_range
    return "UnKnown Color", None

def rgb_color_detection(color_center1, color_center2):
    color_center1 = tuple(color_center1)
    color_center2 = tuple(color_center2)
    color1, color_range1 = get_lower_upper_range(color_center1)
    color2, color_range2 = get_lower_upper_range(color_center2)
    return (color1, color_range1), (color2, color_range2)

def get_hsv_range(hsv_point):
    diff = 10
    mul = 0.7
    r, g, b =tuple(hsv_point)
    lower = (int(r-diff), int(round(g*mul)), 20)
    upper = (int(r+diff), 255, 255)
    return lower, upper

