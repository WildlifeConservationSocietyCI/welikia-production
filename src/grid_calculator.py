import numpy as np
import pandas as pd
import os
from datetime import date

# DIRECTORIES
PROJECT_DIR = r"C:\Users\jesse\PycharmProjects\grid_calculator"
OUT_DIR = os.path.join(PROJECT_DIR, "csv")
date = date.today().strftime("%Y-%m-%d")
UTM_ZONE = "zone18N"
grid_corners_filename = os.path.join(OUT_DIR, "welikia_atlas_grid_coordinates_{}_{}.csv".format(UTM_ZONE, date))
center_points_filename = os.path.join(OUT_DIR, "welikia_atlas_grid_center_points_{}_{}.csv".format(UTM_ZONE, date))

# PARAMETERS

# Scale
page_scale = 1
map_scale = 24000

# meters/inch
m_in_conversion = 0.0254

page_margin = .5

# plate x dimensions
page_size_in_x = 10
page_size_in_x_margin = page_size_in_x - (page_margin * 2)
inches_reality_x = page_size_in_x_margin * map_scale
meters_reality_x = inches_reality_x * m_in_conversion
grid_per_page_x = 5
grid_dimension_x = meters_reality_x / grid_per_page_x

# plate y dimensions
page_size_in_y = 12
page_size_in_y_margin = page_size_in_y - (page_margin * 2)
inches_reality_y = page_size_in_y_margin * map_scale
meters_reality_y = inches_reality_y * m_in_conversion
grid_per_page_y = 6
grid_dimension_y = meters_reality_y / grid_per_page_y

# plate_dimensions = np.Data

num_plates_x = 12
num_plates_y = 10

alphabet = {1:'A', 2:'B', 3:'C', 4:'D', 5:'E', 6:'F', 7:'G', 8:'H', 9:'I', 10:'J', 11:'K', 12:'L', 13:'M', 14:'N', 15:'O', 16:'P', 17:'Q', 18:'R', 19:'S', 20:'T', 21:'U', 22:'V', 23:'W', 24:'X', 25:'Y', 26:'Z'}

# Starting coordinates (x,y) (upper left) UTM
starting_coord = (552800.00, 4536955.60)

grid_ltr = [alphabet[key] for key in [i for i in range(1, grid_per_page_x + 1)]]
grid_num = [i for i in range(1, grid_per_page_y + 1)]
corner = ["UL", "UR", "LR", "LL"]


# [X1,Y1]----------[X2,Y1]
#    |[UL]        [UR]|
#    |                |
#    |                |
#    |                |
#    |                |
#    |                |
#    |[LL]        [LR]|
# [X1,Y2]----------[X2,Y2]

d = []
center_points = []

# X1 = starting_coord[0]
# X2 = starting_coord[0] + grid_dimension_x
# Y1 = starting_coord[1]
# Y2 = starting_coord[1] - grid_dimension_y
# plate_origins = {1: starting_coord}
plates = num_plates_x * num_plates_y
plate = 1
while plate < plates:
    for plate_y in range(1, num_plates_y + 1):
        plate_origin_y = starting_coord[1] - ((plate_y - 1) * meters_reality_y)
        for plate_x in range(1, num_plates_x + 1):
            plate_origin_x = starting_coord[0] + ((plate_x - 1) * meters_reality_x)
            Y1 = plate_origin_y
            Y2 = plate_origin_y - grid_dimension_y
            for num in grid_num:
                X1 = plate_origin_x
                X2 = plate_origin_x + grid_dimension_x
                for ltr in grid_ltr:
                    center_points.append(
                                            {
                                                "Plate": plate,
                                                "Grid": "{}{}".format(ltr, num),
                                                "Letter": ltr,
                                                "Number": num,
                                                "UTMx": X1 + (grid_dimension_x/2),
                                                "UTMy": Y1 - (grid_dimension_y/2)
                                            }
                                        )
                    for c in corner:
                        if c == "UL":
                            UTMx = X1
                            UTMy = Y1
                            Startx = X1
                            Starty = Y1
                            Endx = X2
                            Endy = Y1
                        elif c == "UR":
                            UTMx = X2
                            UTMy = Y1
                            Startx = X2
                            Starty = Y1
                            Endx = X2
                            Endy = Y2
                        elif c == "LL":
                            UTMx = X1
                            UTMy = Y2
                            Startx = X1
                            Starty = Y2
                            Endx = X1
                            Endy = Y1
                        else:
                            UTMx = X2
                            UTMy = Y2
                            Startx = X2
                            Starty = Y2
                            Endx = X1
                            Endy = Y2
                        d.append(
                                    # {"{}{}{}".format(plate,num,ltr) :
                                        {
                                        "Plate": plate,
                                        "Grid": "{}{}".format(ltr,num),
                                        "Letter": ltr,
                                        "Number": num,
                                        "Corner": c,
                                        "UTMx": UTMx,
                                        "UTMy": UTMy,
                                        "Startx":Startx,
                                        "Starty" :Starty,
                                        "Endx": Endx,
                                        "Endy": Endy
                                        }
                                    # }
                                )
                    X1 = X2
                    X2 = X2 + grid_dimension_x
                Y1 = Y2
                Y2 = Y2 - grid_dimension_y
            print(plate)
            plate += 1

#save dataframes as csv
grid_df = pd.DataFrame(d)
grid_df.to_csv(grid_corners_filename)

center_point_df = pd.DataFrame(center_points)
center_point_df.to_csv(center_points_filename)
