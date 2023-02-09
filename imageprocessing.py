import cv2
import numpy as np

# Load the image
img = cv2.imread("Prueba.png")
print(type(img))

# Define the region you want to keep in color
mask = np.zeros(img.shape[:2], dtype="uint8")
mask[200:300, 200:300] = 255

# Convert the rest of the image to grayscale
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img_gray = np.repeat(img_gray[..., np.newaxis], 3, axis=-1)

# Multiply the color region by a factor of 2
color_region = cv2.bitwise_and(img, img, mask=mask) * 2
color_region = np.clip(color_region, 0, 255).astype("uint8")

# Merge the grayscale and color regions
img_result = color_region + cv2.bitwise_and(
    img_gray, img_gray, mask=cv2.bitwise_not(mask)
)

# Show the result
cv2.imshow("Mixed Color and Grayscale", img_result)
cv2.waitKey(0)
cv2.destroyAllWindows()
