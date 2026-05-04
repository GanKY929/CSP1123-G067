from PIL import Image

img = Image.open("METHOD_A/MMU.png")
print(img.format, img.size, img.mode)

img.show()