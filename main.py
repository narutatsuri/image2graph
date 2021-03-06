from util import *
from PIL import Image
import numpy as np
import os
from scipy.spatial import KDTree
from webcolors import CSS3_HEX_TO_NAMES, hex_to_rgb
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline, CubicSpline


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
    img = Image.open(test_imgs_dir + os.fsdecode(f)).transpose(Image.FLIP_TOP_BOTTOM)
    colors_in_img = set()
    color_pixel_coors = {}
    
    for ind_row in range(img.size[0]):
        for ind_col in range(img.size[1]):
            #TODO: Improve this part
            # Naive method:
            #pixel_rgb = img.getpixel((ind_row, ind_col))[:-1]
            #color = get_rgb_name(pixel_rgb)
            #colors_in_img.add(color)
            #if color not in color_pixel_coors:
            #    color_pixel_coors[color] = [[ind_row, ind_col]]
            #else:
            #    color_pixel_coors[color].append([ind_row, ind_col])
            
            # Use KDTree to get specific name:
            color = names[kdt_db.query(img.getpixel((ind_row, ind_col))[:-1])[1]]
            colors_in_img.add(color)
            if color not in color_pixel_coors:
                color_pixel_coors[color] = [[ind_row, ind_col]]
            else:
                color_pixel_coors[color].append([ind_row, ind_col])
                
    # Remove noise; count number of points in color, if less than threshold 
    # remove from dict:
    #TODO: Implement better threshold calculator
    color_count_threshold = min(img.size[0], img.size[1])/2
        
    delete = [color for color in color_pixel_coors if 
              len(color_pixel_coors[color]) < color_count_threshold]
 
    for color in delete: del color_pixel_coors[color]
    
    # Get user input:
    print("There were ", len(color_pixel_coors), " colors detected.")
    print("Choose graph color:")
    for color in color_pixel_coors:
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
    
    s = CubicSpline(x=get_column(formatted_points, 0), y=get_column(formatted_points, 1))
    xs = get_column(formatted_points, 0)
    ys = s(get_column(formatted_points, 0))
    
    print(s.c)
    
    #plt.scatter(get_column(formatted_points, 0), get_column(formatted_points, 1))
    plt.plot(xs, ys)    
    plt.show()
    
    