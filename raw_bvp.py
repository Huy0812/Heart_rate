import cv2

def raw_bvp(image, mask):
    channels = cv2.mean(image, mask)
    mean_green = channels[1]
    return mean_green
    