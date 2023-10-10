import datetime
import matplotlib.pyplot as plt
import numpy as np
import os

from matplotlib.colors import ListedColormap

import json

SensorIds = [

    258, 514, 770, 0, 0, 0, 0, 0, 0, 0, 0, 3074, 3330,
    259, 515, 771, 1027, 1283, 1539, 1795, 2051, 2307, 2563, 2819, 3075, 3331,
    260, 516, 772, 1028, 1284, 1540, 1796, 2052, 2308, 2564, 2820, 3076, 3332,
    261, 517, 773, 1029, 1285, 1541, 1797, 2053, 2309, 2565, 2821, 3077, 3333,
    262, 518, 774, 0, 0, 0, 1798, 0, 2310, 0, 2822, 3078, 3334,
    263, 519, 775, 1031, 1287, 1543, 1799, 2055, 2311, 0, 2823, 3079, 3335,
    264, 520, 776, 0, 0, 0, 1800, 0, 2312, 0, 2824, 3080, 3336,
    265, 521, 777, 1033, 1289, 1545, 1801, 2057, 2313, 2569, 2825, 3081, 3337,
    266, 522, 778, 1034, 1290, 1546, 1802, 2058, 2314, 2570, 2826, 3082, 3338,
    267, 523, 779, 1035, 1291, 1547, 1803, 2059, 2315, 2571, 2827, 3083, 3339,

]


def fetch_message(folder_path):
    json_data = []

    # Check if the folder path exists
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return json_data

    # List all files in the folder
    files = os.listdir(folder_path)

    for file_name in files:
        file_path = os.path.join(folder_path, file_name)

        # Check if the file is a JSON file
        if file_name.endswith('.json') and os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    json_data.append(data)

            except Exception as e:
                print(f"Error loading data from '{file_name}': {e}")

    return json_data


def fetch_Data(loaded_data):
    Modids = []
    Date = []
    Data = (Modids, Date)
    # print(len(loaded_data))
    for data in loaded_data:
        Modids.append((int(data['MODID'][:2], 16) - 1, int(data['MODID'][2:], 16) - 2))
        Date.append(data['event_millis'])
    # print(len(Modids),len(Date))

    return Data


def generate_grid():
    ROWS = 10
    COLUMNS = 13
    grid = np.zeros((ROWS, COLUMNS), dtype=object)

    count = -1
    for i in range(ROWS):
        for j in range(COLUMNS):
            count += 1
            cell_info = {
                'SensorId': SensorIds[count],
                'Number_of_Activations': 0,
                'Date': None
            }
            grid[i, j] = cell_info

    return grid


def generate_visualization_grid(grid):
    ROWS, COLUMNS = grid.shape
    vis_grid = np.zeros((ROWS, COLUMNS))

    for i in range(ROWS):
        for j in range(COLUMNS):
            cell_info = grid[i, j]
            vis_info = cell_info['Number_of_Activations']
            vis_grid[i, j] = vis_info

    return vis_grid


def apply_info(data, grid):
    cell_info_list = []

    for count, (x, y) in enumerate(data[0]):
        cell_info = grid[y, x]

        cell_info['Number_of_Activations'] += 1
        cell_info['Date'] = data[1][count]
        cell_info_list.append(cell_info)

        plot_grid(cell_info_list, generate_visualization_grid(grid))

    calc_recent_activation(cell_info_list)


def calc_recent_activation(applied_grid):
    
    ...


def plot_grid(applied_grid, grid, highlight_condition):
    info_grid = (applied_grid, grid)
    print(info_grid)

    # x and y axis is swapped
    custom_colors = [(255, 245, 235), (254, 230, 206), (253, 208, 162), (253, 174, 107),
                     (253, 141, 60), (241, 105, 19), (217, 72, 1), (166, 54, 3), (127, 39, 4)]
    normalized_colors = [(r / 255, g / 255, b / 255) for r, g, b in custom_colors]
    custom_cmap = ListedColormap(normalized_colors)
    fig, ax = plt.subplots()
    vis_grid = grid[::-1]
    n, m = vis_grid.shape


    cax = ax.imshow(vis_grid, cmap=custom_cmap, interpolation='none', aspect='auto')
    # plt.imshow(np.ones_like(grid), cmap='binary', interpolation='none', aspect='auto')
    plt.xticks([])  # Hide x-axis ticks
    plt.yticks([])  # Hide y-axis ticks
    # print(vis_grid)

    for i in range(n):
        for j in range(m):
            cell_value = int(vis_grid[i, j])
            if highlight_condition(i, j):
                cell_color = 'black'
                cell_edgecolor = 'purple'  # Set the outline color to purple for every second cell
            else:
                cell_color = 'black'
                cell_edgecolor = 'white'  # Set the outline color to white for other cells
            plt.text(j, i, cell_value, ha='center', va='center', color=cell_color, fontsize=8)
            rect = plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor=cell_edgecolor)
            ax.add_patch(rect)

    # Add spacing between squares
    for i in range(1, n):
        plt.axhline(i - 0.5, color='black', lw=0.5, linestyle='--')
    for j in range(1, m):
        plt.axvline(j - 0.5, color='black', lw=0.5, linestyle='--')


    title_key = 'Date'
    print(info_grid[0][-1])
    #print(info_grid[0][title_key])
    # real_time = datetime.datetime.fromtimestamp(info_grid[1][1][title_key])
    plt.title(f'{info_grid[0][-1][title_key]}')
    # plt.text(5, 10, real_time, fontsize=14)

    folder_name = 'pictures'
    current_msg = -1

    file_name = f"{info_grid[0][-1][title_key]}_lol.png"
    file_path = os.path.join(folder_name, file_name)

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    plt.savefig(file_path)


if __name__ == "__main__":
    folder_path = 'json'
    loaded_data = fetch_message(folder_path)

    modifications = fetch_Data(loaded_data)
    grid = generate_grid()

    apply_info(modifications, grid)
    # calc_recent_activation(applied_grid)



