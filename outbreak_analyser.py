"""
Outbreak Analyser

Description:
This script analyzes the outbreak of an airborne pathogen based on the locations of reported cases
and a gridded representation of the population. It determines the outbreak center, calculates the affected
population, and visualizes the population distribution with the outbreak center.

Usage:
python outbreak_analyser.py

Requirements:
- Python 3.x
- NumPy
- Matplotlib

Input Files:
1. case_locations.csv: Case line list dataset with X and Y coordinates of patient locations.
2. population.csv: Gridded representation of the population for the area concerned.

Outputs:
- Console output with outbreak center, total population, affected population, and percentage affected.
- Population distribution plot with the outbreak center saved as "outbreak_plot.png".

Note:
This script assumes the pathogen spreads evenly in all directions forming a circle.


Author: Babak Mahdavi Ardestani
Date: 11 Jan 2024


"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import os

def load_data(file_name, directory="data", skip_header=True):
    """
    Load data from a CSV file in the specified directory.

    Parameters:
    - file_name (str): Name of the CSV file.
    - directory (str): Directory containing the CSV file. Default is "data".
    - skip_header (bool): Whether to skip the first row as a header. Default is True.

    Returns:
    - numpy.ndarray: Loaded data.
    """
    file_path = os.path.join(directory, file_name)
    return np.loadtxt(file_path, skiprows=1 if skip_header else 0, delimiter=',')


def plot_population(population_matrix, outbreak_centre, output_dir=None, fig_name=None):
    """
    Plot population distribution and outbreak center.

    Parameters:
    - population_matrix (numpy.ndarray): Matrix representing population distribution.
    - outbreak_centre (numpy.ndarray): Coordinates of the outbreak center.
    - output_dir (str): Optional. If provided, the plot will be saved in this directory.
    - fig_name (str): Optional. If provided, the plot will be saved with the given file name.

    Returns:
    - None
    """
    # Exclude zero or negative values for LogNorm
    non_negative_matrix = np.where(population_matrix <= 0, 1, population_matrix)
    
    plt.imshow(non_negative_matrix, cmap='jet', origin='lower', norm=LogNorm())
    plt.colorbar(label='Population (log scale)')
    plt.scatter(outbreak_centre[0] / 100, outbreak_centre[1] / 100, marker='o', color='black', label='Outbreak Center')
    plt.title('Population Distribution & Outbreak Center (log scale)')
    plt.xlabel('East-West (100m per cell)')
    plt.ylabel('North-South (100m per cell)')

    # Adjust label position by changing the 'xy' parameter
    #plt.text(outbreak_centre[0] / 100 + 5, outbreak_centre[1] / 100 + 5, 'Outbreak Center', color='black')
    
    #plt.legend()
    #plt.legend(loc='upper left')  # Adjust the location here
    #plt.legend(loc='upper right', bbox_to_anchor=(0.45, 0.9))
    plt.legend(loc='upper right', bbox_to_anchor=(1, 0.6), fontsize='small')

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)  # Create the output directory if it doesn't exist

    if fig_name:
        if output_dir:
            fig_path = os.path.join(output_dir, fig_name)
        else:
            fig_path = fig_name

        plt.savefig(fig_path, bbox_inches='tight')  # Save the plot as a PNG file
        plt.close()  # Close the plot to avoid displaying it if plt.show() is called later
    else:
        plt.show()

def calculate_distance_matrix(locations):
    """
    Calculate the distance matrix between locations.

    Parameters:
    - locations (numpy.ndarray): Array containing X and Y coordinates.

    Returns:
    - numpy.ndarray: Distance matrix.
    """
    x_diff = locations[:, 1].reshape(-1, 1) - locations[:, 1]
    y_diff = locations[:, 2].reshape(-1, 1) - locations[:, 2]
    distance_matrix = np.sqrt(x_diff ** 2 + y_diff ** 2)
    return distance_matrix

def find_outbreak_centre(locations):
    """
    Find the outbreak center based on the maximum distance between cases.

    Parameters:
    - locations (numpy.ndarray): Array containing X and Y coordinates.

    Returns:
    - numpy.ndarray: Coordinates of the outbreak center.
    """
    distance_matrix = calculate_distance_matrix(locations)
    max_distance_index = np.unravel_index(np.argmax(distance_matrix), distance_matrix.shape)
    outbreak_centre = locations[max_distance_index[0], 1:3]
    return outbreak_centre

def find_affected_population(population_matrix, outbreak_centre, max_distance):
    """
    Find the affected population within the specified range of the outbreak center.

    Parameters:
    - population_matrix (numpy.ndarray): Matrix representing population distribution.
    - outbreak_centre (numpy.ndarray): Coordinates of the outbreak center.
    - max_distance (float): Maximum distance from the outbreak center.

    Returns:
    - float: Affected population.
    """
    east_west_cells, north_south_cells = population_matrix.shape
    cell_size = 100  # meters per cell

    outbreak_centre_cells = outbreak_centre / cell_size

    east_west_range = int(max_distance / cell_size)
    north_south_range = int(max_distance / cell_size)

    start_i = max(0, int(outbreak_centre_cells[0] - east_west_range))
    end_i = min(east_west_cells, int(outbreak_centre_cells[0] + east_west_range + 1))

    start_j = max(0, int(outbreak_centre_cells[1] - north_south_range))
    end_j = min(north_south_cells, int(outbreak_centre_cells[1] + north_south_range + 1))

    affected_population = np.sum(population_matrix[start_i:end_i, start_j:end_j])

    return affected_population

# Load data from the "data" directory
case_locations = load_data("case_locations.csv")
population_matrix = load_data("population.csv", skip_header=False)

# Find outbreak centre
outbreak_centre = find_outbreak_centre(case_locations)
print("Outbreak Centre:", outbreak_centre)

# Calculate maximum distance
max_distance = np.max(calculate_distance_matrix(case_locations))

# Find affected population
affected_population = find_affected_population(population_matrix, outbreak_centre, max_distance)

# Calculate total population size
total_population = np.sum(population_matrix)

# Calculate percentage affected
percentage_affected = (affected_population / total_population) * 100

# Print the results
print("Total Population: ~", round(total_population))
print("Affected Population: ~", round(affected_population))
print("Percentage Affected: {:.2f}%".format(percentage_affected))

# Plot population distribution with outbreak center and save the plot in the "output" directory
plot_population(population_matrix, outbreak_centre, output_dir="output", fig_name="outbreak_plot.png")


