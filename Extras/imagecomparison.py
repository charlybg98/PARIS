import cv2
import numpy as np
import os

path_to_prog = os.path.join("2023-02-01", "Full")
path_to_save = os.path.join("2023-02-01", "Processed")


def mse(img1, img2):
    h, w = img1.shape
    diff = cv2.subtract(img1, img2)
    err = np.sum(diff**2)
    mse = err / (float(h * w))
    return mse, diff


for image in os.listdir(path_to_prog):
    print(os.path.join(path_to_prog, image))
    img1 = cv2.imread(os.path.join(path_to_prog, image))
    img2 = cv2.imread("Base.png")
    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    error, diff = mse(img2, img1)
    cv2.imwrite(os.path.join(path_to_save, image), diff)


# cv2.imshow("difference", diff)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
