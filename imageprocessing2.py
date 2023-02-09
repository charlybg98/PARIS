import cv2
import numpy as np

# Cargar la imagen
image_path = "824 102 18_6_53.png"
img = cv2.imread(image_path)
print("Shape of original image:", img.shape)

x, y = image_path.split()[:-1]
x, y = int(x), int(y)

# Crear una máscara para la región donde se ha realizado la acción
mask = np.zeros(img.shape[:2], dtype=np.uint8)

# Aquí se debe especificar la región en la que se ha realizado la acción.
# Por ejemplo, si se ha hecho clic en un botón en la coordenada (x, y),
# la máscara se puede definir como:
mask[y - 10 : y + 10, x - 10 : x + 10] = 255


# Crear una imagen en la que la región destacada sea de un color diferente
img_highlight = img.copy()
img_highlight[mask != 0] = (0, 0, 255)  # color rojo

# Dibujar un rectángulo alrededor de la región destacada
x, y, w, h = cv2.boundingRect(mask)
cv2.rectangle(img_highlight, (x, y), (x + w, y + h), (0, 255, 0), 2)

# Mostrar la imagen resultante
cv2.imshow("Highlighted Image", img_highlight)
cv2.waitKey(0)
cv2.destroyAllWindows()
