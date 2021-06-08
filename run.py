# First let's import some dependencies

import os, sys      # for OS utilities
import numpy as np  # for some mathematical transformations
import cv2          # mainly for Histogram equalization
from PIL import Image, ImageFont, ImageDraw 
                    # Sadly, openCV does not support writing any mono-space fonts.
                    # So, we have to use Pillow to load custom TTF(True Type Font) files.


def main():

    # In case, user wants to change the font-size of the ASCII image, this varible should be changed.
    # WARNING: Do not set font-size < 5, else the program may get stuck in infinite loop.
    fontSize = 8    
    if fontSize < 5:
        print("WARNING: Font-Size is too small. This may result in infinite-loop. Enter any key to continue.")
        _ = input()

    CHAR_MAP = [temp for temp in reversed("""$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/|(1{[?-_+~<i!lI;:,"^`'. """)]
    # The characters in the above string are sorted according to the amount of white they cover in mono-space fonts.
    # Monospace fonts are those fonts which use the same width no matter the character printed. They are convenient to use for ASCII-art.
    # There are some versions that have minor differences, I am using the one from : http://paulbourke.net/dataformats/asciiart/
    

    # Let's specify some paths
    INPUT_PATH = sys.argv[1]    # Input image path to be provided as a comman-line argument
    OUTPUT_PATH = "out.png"     # This is where output image will be stored

    # We are using the mono-space fonts called "secret-code" from Matthew Welch (https://squaregear.net/fonts/)
    # I have added a copy of the font and liscence files in this repository, these fonts are published under MIT liscence.
    FONT_PATH = os.path.join("secret_code", "secrcode.ttf") 
    
    OUTPUT_WINDOW_NAME = "ASCIIfied"     # Name for the output window

    
    # Let's read the input image and get its dimensions
    image = cv2.imread(INPUT_PATH)
    image_height, image_width, _ = image.shape
    
    # Now we load the font file and get the height and width for each font
    font = ImageFont.truetype(FONT_PATH, fontSize)
    font_width, font_height = font.getsize(".")

    # We convert the BGR image to HSV and normalize Saturation and Value channels before converting image back to RGB.
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # uncomment the below lines in case you want to apply Hist-equalization before the ASCIIfication as well.
    # hsv_image[..., 1] = cv2.equalizeHist(hsv_image[..., 1])
    # hsv_image[..., 2] = cv2.equalizeHist(hsv_image[..., 2])
    
    rgb_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2RGB)


    # Output blank canvas
    output = np.zeros_like(image)

    pillow_output = Image.fromarray(output)
    pillow_drawer = ImageDraw.Draw(pillow_output)
    for i in range(int(image_height / font_height)):
        for j in range(int(image_width / font_width)):

            # finding the bounding box for the next character to be inserted
            y_start = i*font_height
            x_start = j*font_width

            x_end = x_start + font_width
            y_end = y_start + font_height

            # deciding the next character to be inserted
            i1 = np.mean(hsv_image[y_start:y_end, x_start:x_end, 1])
            i2 = np.mean(hsv_image[y_start:y_end, x_start:x_end, 2])
            intensity = (i1 +i2)/2

            position = int(intensity * len(CHAR_MAP) / 360)

            # deciding the color of the next character
            color = np.mean(rgb_image[y_start:y_end, x_start:x_end], axis = (0, 1)).astype(np.uint8)
            # uncomment the below line if you want same color for each character
            # color = (255, 255, 255)
            
            # inserting the next character
            pillow_drawer.text((x_start, y_start), str(CHAR_MAP[position]), font = font, fill=tuple(color))
            # uncomment the below line if you want same character and only vary its color
            # pillow_drawer.text((x_start, y_start), "*", font = font, fill=tuple(color))

    # Converting back to OpenCV
    output = np.array(pillow_output)


    # Performing Histogram Equalization on S and V channels of the output to improve sharpness.    
    output_hsv = cv2.cvtColor(output, cv2.COLOR_RGB2HSV)

    output_hsv[..., 1] = cv2.equalizeHist(output_hsv[..., 1])
    output_hsv[..., 2] = cv2.equalizeHist(output_hsv[..., 2])
    
    output_bgr = cv2.cvtColor(output_hsv, cv2.COLOR_HSV2BGR)

    # Show Output on screen and write it to a file
    cv2.imshow(OUTPUT_WINDOW_NAME, output_bgr)
    cv2.imwrite(OUTPUT_PATH, output_bgr)
    
    # Wait till Key-press for exit
    cv2.waitKey(0)

if __name__ == "__main__":
    main()