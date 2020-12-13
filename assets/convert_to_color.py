import os
from PIL import Image
dir = "C:\\Users\\Jtwal\\Desktop\\Snake Pygame\\assets\\"
files = os.listdir(dir)
color = "green_"
to_color = "yellow_"
color_val = (22,164,22,255)
to_color_val = (255,255,0,255)
for file in files:
	if file.find(color) != -1:
		im = Image.open(dir + file)
		pixelMap = im.load()
		img = Image.new(im.mode,im.size)
		pixelsNew = img.load()
		for i in range(img.size[0]):
			for j in range(img.size[1]):
				if pixelMap[i,j] == color_val:
					pixelsNew[i,j] = to_color_val
				else:
					pixelsNew[i,j] = pixelMap[i,j]
		img.save(dir + to_color + file[len(color):])

