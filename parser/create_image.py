import matplotlib.pyplot as plt
import numpy as np


def generate_grid(n, m):
    grid = np.zeros((n, m))  # Initialize an n x m grid with zeros
    for i in range(n):
        for j in range(m):
            grid[i, j] = i * m + j + 1  # Enumerate each square

    return grid


def plot_grid(grid):
    n, m = grid.shape
    plt.imshow(np.ones_like(grid), cmap='viridis', interpolation='none', aspect='auto')
    plt.xticks([])  # Hide x-axis ticks
    plt.yticks([])  # Hide y-axis ticks

    for i in range(n):
        for j in range(m):
            plt.text(j, i, grid[i, j], ha='center', va='center', color='black', fontsize=8)

    # Add spacing between squares
    for i in range(1, n):
        plt.axhline(i - 0.5, color='black', lw=0.5, linestyle='--')
    for j in range(1, m):
        plt.axvline(j - 0.5, color='black', lw=0.5, linestyle='--')

    plt.show()


n = 10  # Number of rows
m = 13  # Number of columns

grid = generate_grid(n, m)
plot_grid(grid)
