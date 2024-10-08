from dataclasses import dataclass
import drawsvg as draw
from math import floor, comb
import matplotlib.pyplot as plt
from tqdm import tqdm
from scipy.interpolate import splrep, splev

import numpy as np


k_e = 8.99e9  # Coulomb constant in N·m²/C²
STEP_SIZE = 0.01
NUM_LINES = 10
XRANGE = (-2, 2)
YRANGE = (-2, 2)
WIDTH = 1600*1
HEIGHT = 1200*1
MAX_STEP_SIZE = 0.1

LINE_COLOUR = "white"
BACKGROUND_COLOUR = "pink"
RADIUS = 40
LINE_WIDTH = 5

def in_range(x, y, x_range, y_range):
    x_min = x_range[0]
    x_max = x_range[1]
    y_min = y_range[0]
    y_max = y_range[1]
    if x_min <= x <= x_max and y_min <= y <= y_max:
        return True
    return False


def map_to_image_coords(x, y, xrange, yrange, width, height):
    xmin = xrange[0]
    xmax = xrange[1]
    ymin = yrange[0]
    ymax = yrange[1]

    u = floor((x - xmin) / (xmax - xmin) * width)
    v = floor((y - ymin) / (ymax - ymin) * height)
    u = min(max(u, 0), width - 1)
    v = min(max(v, 0), height - 1)
    return u, v


def follow_field_lines(
    start_point,
    Ex,
    Ey,
    x,
    y,
    width=WIDTH,
    height=HEIGHT,
    step_size=STEP_SIZE,
    forwards=True,
):
    x_pos, y_pos = start_point
    points = []

    E_log = np.log(np.max(np.sqrt(Ex**2 + Ey**2) + 1e-10)) 
    upper_bound = np.exp(0.7 *E_log) - 1e-10

    if forwards:
        direction = 1
    else:
        direction = -1
    try:
        while True:
            # Get the nearest grid indices
            x_index = np.clip(np.searchsorted(x, x_pos), 0, width - 1)
            y_index = np.clip(np.searchsorted(y, y_pos), 0, height - 1)

            # Get the electric field at the current position
            Ex_value = Ex[y_index, x_index]
            Ey_value = Ey[y_index, x_index]
            E_magnitude = np.sqrt(Ex_value**2 + Ey_value**2)

            #print(E_magnitude)
            # Check if the electric field is negligible or we are out of bounds
            #if E_magnitude > upper_bound or not in_range(x_pos, y_pos, XRANGE, YRANGE):
            if not in_range(x_pos, y_pos, XRANGE, YRANGE):
                #
                break

            # Store the current point in grid coordinates
            points.append((x_pos, y_pos))

            # Update position using Euler's method
            if abs(Ex_value * step_size) > MAX_STEP_SIZE:
                x_step = MAX_STEP_SIZE * np.sign(Ex_value)
            else:
                x_step = Ex_value * step_size
            
            if abs(Ey_value * step_size) > MAX_STEP_SIZE:
                y_step = MAX_STEP_SIZE * np.sign(Ey_value)
            else: 
                y_step = Ey_value * step_size 

            x_pos += direction * x_step
            y_pos += direction * y_step
    except Exception as e:
        print(e)
    return points


def add_point_charge(X, Y, q, pos):
    """
    Adds the electric field from a point charge to the grid.

    Parameters:
    q -- Charge of the point particle.
    pos -- Position of the charge as a tuple (x, y).
    """
    # Position of the charge
    x_charge, y_charge = pos

    # Distance vectors from the charge to every point in the grid
    dx = X - x_charge
    dy = Y - y_charge
    r = np.sqrt(dx**2 + dy**2)  # Radial distance

    # Avoid division by zero at the location of the charge
    r[r == 0] = np.inf

    # Coulomb's law: E = k_e * q / r^2
    E = k_e * q / r**2

    # Field components in x and y directions
    Ex = E * dx / r  # E_x = E * cos(theta) = E * (dx / r)
    Ey = E * dy / r  # E_y = E * sin(theta) = E * (dy / r)

    return Ex, Ey


if __name__ == "__main__":

    x_vector = np.linspace(XRANGE[0], XRANGE[1], WIDTH)
    y_vector = np.linspace(YRANGE[0], YRANGE[1], HEIGHT)
    X, Y = np.meshgrid(x_vector, y_vector)

    Ex = np.zeros((HEIGHT, WIDTH))
    Ey = np.zeros((HEIGHT, WIDTH))

    charges = [
        {"position": (1, 0), "charge": 1e-9},  # Positive charge
        {"position": (-1, 0), "charge": -1e-9},  # Negative charge
    ]

    for charge in charges:

        Ex_c, Ey_c = add_point_charge(
            X, Y, charge["charge"], charge["position"]
        )  # Positive charge at (1, 0)
        Ex += Ex_c
        Ey += Ey_c

    d = draw.Drawing(WIDTH, HEIGHT)
    d.append(draw.Rectangle(0, 0, WIDTH, HEIGHT, fill=BACKGROUND_COLOUR))

    x_min, x_max = XRANGE
    y_min, y_max = YRANGE

    initial_points = []
    for x_center in [x_min, (x_min + x_max) / 2, x_max]:
        y_center = np.linspace(y_min, y_max, NUM_LINES)  # Linearly spaced y values
        vertical_line_points = np.column_stack((np.full(NUM_LINES, x_center), y_center))
        initial_points.append(vertical_line_points)
    for y_center in [y_min, y_max]:
        x_center = np.linspace(x_min, x_max, NUM_LINES)  # Linearly spaced x values
        horizontal_line_points = np.column_stack((x_center, np.full(NUM_LINES, y_center)))
        initial_points.append(horizontal_line_points)

    
    initial_points = np.vstack(initial_points)

    for initial_point in tqdm(initial_points, desc="Processing Points"):
        # Follow field lines forwards and backwards
        for forwards in [True, False]:
            accumulated_points = follow_field_lines(
                initial_point, Ex, Ey, x_vector, y_vector, forwards=forwards
            )

            if not len(accumulated_points) == 0:
                # Get a path object
                p = draw.Path(stroke=LINE_COLOUR, fill="none", stroke_width=LINE_WIDTH)
                # Downsample points
                num_downsampled_points = 20
                if len(accumulated_points) <= num_downsampled_points:
                    downsampled_points = accumulated_points
                else:
                    step = len(accumulated_points) / float(num_downsampled_points)
                    downsampled_points = [
                        accumulated_points[int(i * step)]
                        for i in range(num_downsampled_points)
                    ]

                # move to the first point
                x, y = downsampled_points[0]
                u, v = map_to_image_coords(x, y, XRANGE, YRANGE, WIDTH, HEIGHT)
                p.M(u, v)

                for i in range(1, len(downsampled_points) - 2, 3):
                    x, y = downsampled_points[i]
                    u, v = map_to_image_coords(x, y, XRANGE, YRANGE, WIDTH, HEIGHT)
                    x_, y_ = downsampled_points[i + 1]
                    u_, v_ = map_to_image_coords(x_, y_, XRANGE, YRANGE, WIDTH, HEIGHT)
                    x__, y__ = downsampled_points[i + 2]
                    u__, v__ = map_to_image_coords(
                        x_, y_, XRANGE, YRANGE, WIDTH, HEIGHT
                    )

                    p.C(u, v, u__, v__, u_, v_)

                d.append(p)

    for charge in charges:
        pos = charge["position"]

        # Map the position to image coordinates
        u, v = map_to_image_coords(pos[0], pos[1], XRANGE, YRANGE, WIDTH, HEIGHT)

        # d.append(draw.Circle(u, v, r=RADIUS, fill=BACKGROUND_COLOUR, opacity=1))  # r is the radius

    d.save_svg("electric-field-lines.svg")

    plt.figure(figsize=(6, 6))
    plt.streamplot(X, Y, Ex, Ey, color="blue")
    plt.title("Electric Field Lines")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.savefig("electric_field.png")

    E_magnitude = np.sqrt(Ex**2 + Ey**2)
    E_normalized = E_magnitude / np.max(E_magnitude)
    E_corrected = np.power(E_normalized, 0.2) * np.max(E_normalized)
    plt.imshow(E_corrected)

    plt.savefig("field_strength.png")
