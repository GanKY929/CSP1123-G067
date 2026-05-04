from PIL import Image
from urllib.request import urlopen

img_url = "https://i.pinimg.com/236x/a0/c8/66/a0c866248f26735b9249486aade308eb.jpg"
img = Image.open(urlopen(img_url))
print(img.format, img.size, img.mode)

img.show()
