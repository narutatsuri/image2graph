from util import *
from PIL import Image
import os
from scipy.spatial import KDTree
from webcolors import CSS3_HEX_TO_NAMES, hex_to_rgb
import matplotlib.pyplot as plt


def get_rgb_name(rgb):
    if white_threshold < rgb[0] and white_threshold < rgb[1] and white_threshold < rgb[2]:
        return "white"
    elif black_threshold > rgb[0] and black_threshold > rgb[1] and black_threshold > rgb[2]:
        return "black"
    else:
        if rgb.index(max(rgb)) == 0:
            return "red"
        elif rgb.index(max(rgb)) == 0:
            return "green"
        else:
            return "blue"
        
def get_column(matrix, i):
    return [row[i] for row in matrix]

# Construct KDTree to find closest color name for RGB tuple.
# Credit: https://medium.com/codex/rgb-to-color-names-in-python-the-robust-way-ec4a9d97a01f
css3_db = CSS3_HEX_TO_NAMES
names = []; rgb_values = []
for color_hex, color_name in css3_db.items():
    names.append(color_name)
    rgb_values.append(hex_to_rgb(color_hex))
    
print("Constructing KDTree...")
kdt_db = KDTree(rgb_values)
print("Constructed KDTree.")

# Loop through image directory:
for f in os.listdir(os.fsencode(test_imgs_dir)):
    img = Image.open(test_imgs_dir + os.fsdecode(f))
    colors_in_img = set()
    color_pixel_coors = {}
    
    for ind_row in range(img.size[0]):
        for ind_col in range(img.size[1]):
            # Naive method:
            pixel_rgb = img.getpixel((ind_row, ind_col))[:-1]
            color = get_rgb_name(pixel_rgb)
            colors_in_img.add(color)
            if color not in color_pixel_coors:
                color_pixel_coors[color] = [[ind_row, ind_col]]
            else:
                color_pixel_coors[color].append([ind_row, ind_col])
            
            # Use KDTree to get specific name:
            # colors_in_img.add(names[kdt_db.query(img.getpixel((ind_row, ind_col))[:-1])[1]])
    
    # Get user input:
    print("There were ", len(colors_in_img), " colors detected.")
    print("Choose graph color:")
    for color in colors_in_img:
        print("- ", color)
    color = input()
    while color not in colors_in_img:
        color = input("Invalid input. Try again: ")
          
    # Construct an array where each x coordinate is unique:
    formatted_points = []
    last_pixel_x = color_pixel_coors[color][0][0]
    same_x_sum = color_pixel_coors[color][1][0]; same_x_count = 1
    for pixel in color_pixel_coors[color][1:]:
        if pixel[0] == last_pixel_x:
            same_x_sum += pixel[1]
            same_x_count += 1
        else:
            formatted_points.append([last_pixel_x, int(same_x_sum/same_x_count)])
            last_pixel_x = pixel[0]
            same_x_sum = pixel[1]
            same_x_count = 1
    print(formatted_points)
    
    plt.scatter(get_column(formatted_points, 0), get_column(formatted_points, 1))
    plt.show()