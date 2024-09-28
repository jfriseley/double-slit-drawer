from dataclasses import dataclass
import drawsvg as draw
from math import floor
import matplotlib.pyplot as plt

import numpy as np 


k_e = 8.99e9  # Coulomb constant in N·m²/C²


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


if __name__=="__main__":



    grid_size = 100
    x = np.linspace(-5, 5, grid_size)
    y = np.linspace(-5, 5, grid_size)
    X, Y = np.meshgrid(x, y)

    # Initialize electric field components (Ex and Ey)
    Ex = np.zeros((grid_size, grid_size))
    Ey = np.zeros((grid_size, grid_size))


    # Add a few example charges
    Ex1, Ey1 = add_point_charge(X, Y, 1e-9, (1, 0))  # Positive charge at (1, 0)
    Ex += Ex1 
    Ey += Ey1

    Ex2, Ey2 = add_point_charge(X, Y, -1e-9, (-1, 0))  # Negative charge at (-1, 0)
    Ex += Ex2 
    Ey += Ey2

    # Plot the electric field using quiver
    plt.figure(figsize=(6, 6))
    plt.streamplot(X, Y, Ex, Ey, color='blue')
    plt.title("Electric Field Lines")
    plt.xlabel('X')
    plt.ylabel('Y')

    plt.savefig('electric_field.png')