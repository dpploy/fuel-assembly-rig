import numpy as np
from matplotlib import pyplot as plt
import shutil
import ast
import time
import math
import matplotlib
import datetime

'''
This is a simple plotting tool for visualizing pre-existing MFF data. It can plot thermocouple, SCR control signal 
current, and watt transducer data from text files. 

Thermocouple data is logged in a single file, while SCR current and watt transducer data are logged in the same file. 

'''


def convert_to_unix_timestamp(timestamp):
    """
    Takes timestamps in mm/dd/yyyy hh:mm:ss form and converts to unix timestamp
    """
    (date, input_time) = timestamp.split(" ")

    (month, day, year) = date.split("/")
    (hour, minute, second) = input_time.split(":")
    date_time = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))

    unix_timestamp = time.mktime(date_time.timetuple())
    return unix_timestamp

def gen_twin_plot(data,dynamic=False):
    if dynamic:
        plt.ion()
    (times_list, temp_list, cur_timestamp_list, watt_list) = data[:]
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex="all")
    fig.set_size_inches(15, 8)

    ax1.set_title(f"MFF Thermocouple Data ")
    bundle_colors = ["Purples", "Reds", "Blues", "Greens", "Oranges"]
    for bundle_num in range(5):
        color_map = matplotlib.cm.get_cmap(bundle_colors[bundle_num])

        for couple_num in range(5):
            series_color = color_map((couple_num + 1) / 5)
            ax1.plot(times_list, temp_list[bundle_num][couple_num],
                     label=f"Bundle {bundle_num + 1} Couple {couple_num + 1}", color=series_color)
    plt.xlabel("Time (min)")

    box = ax1.get_position()
    ax1.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax1.set_ylabel("Temperature (°C)")
    ax1.grid()

    """ax2.plot(cur_timestamp_list, cur_list)
    ax2.set_ylabel("Current (mA)")"""

    ax2.plot(cur_timestamp_list, watt_list)
    ax2.set_ylabel("Power (W)")

    box2 = ax2.get_position()
    ax2.set_position([box2.x0, box2.y0, box2.width * 0.8, box2.height])
    ax2.grid()

    #plt.savefig(str(time.time()) + ".png", dpi=300)
    #plt.show()
    new_data = [times_list, temp_list, cur_timestamp_list, watt_list]

    return(ax1,ax2,fig)

def rescan_files(extra_data=False):
    # Copies data files to temporary files
    shutil.copy("Final_Backup_8_12_22_535pm/simplePlotter.txt", "copied_temp_file.txt")
    shutil.copy("../CurrentFile_Aug_11_430pm.txt", "copied_current_file.txt")

    # Initialize data lists
    average_temp_list = []
    ref_temp_list = []
    times_list = []
    temp_list = [
        [[], [], [], [], []],
        [[], [], [], [], []],
        [[], [], [], [], []],
        [[], [], [], [], []],
        [[], [], [], [], []]
    ]

    cur_list = []
    power_transducer_list = []
    cur_timestamp_list = []

    # Import thermocouple data from file
    with open("copied_temp_file.txt", 'r') as f:
        for line in f.readlines():
            line_list = np.asarray(ast.literal_eval(line[19:]))
            times_list.append(line[:19])
            average_temp = np.average(line_list[:20])
            ref_temp = line_list[-1]

            average_temp_list.append(average_temp)
            ref_temp_list.append(ref_temp)

            for couple_num, couple_val in enumerate(line_list):
                bundle_num = math.floor(couple_num / 5)
                temp_list[bundle_num][couple_num - bundle_num * 5].append(couple_val)

    times_list = np.asarray(times_list, dtype=np.int64)
    times_list = times_list / 1e9
    start_time = times_list[0]

    # print("Values greater than runtime are", times_list[times_list > times_list[-1]])
    # print("indices are", np.nonzero(times_list > times_list[-1]))

    # Import current and watt transducer data
    with open("copied_current_file.txt", 'r') as file:
        cur_data = file.readlines()

    for line in cur_data:
        cur_list.append(float(line.split("\t")[0]) * 1000)
        power_transducer_list.append(float(line.split("\t")[1]))
        timestamp = line.split("\t")[-1].strip()[:-3]
        am_or_pm = line[-3:-1]

        unix_timestamp = convert_to_unix_timestamp(timestamp)

        if am_or_pm == "PM" and line[-12:-10] != "12":
            unix_timestamp += 60 * 60 * 12

        cur_timestamp_list.append(unix_timestamp)

    cur_timestamp_list = np.asarray(cur_timestamp_list)
    cur_start_time = cur_timestamp_list[0]
    cur_time_after_temp_start = cur_start_time - start_time

    #print("Current File Start Time:", cur_timestamp_list[0])
    #print("Temperature File Start Time:", start_time)
    # Determine which log file begins at an earlier time and determine time offset
    if cur_time_after_temp_start < 0:
        temp_offset = -cur_time_after_temp_start
        cur_offset = 0
    else:
        temp_offset = 0
        cur_offset = cur_time_after_temp_start

    print("Temperature Offset", temp_offset)
    print("Current Offset", cur_offset)
    # print(cur_start_time, start_time)

    # Normalize timestamps for both data files
    times_list -= (times_list[0] - temp_offset)
    cur_timestamp_list -= (cur_start_time - cur_offset)
    """times_list -= (times_list[0])
    cur_timestamp_list -= (cur_start_time)
    times_list += temp_offset
    cur_timestamp_list += cur_offset"""

    times_list = times_list / 60
    cur_timestamp_list = cur_timestamp_list / 60

    watt_list = np.asarray(power_transducer_list)
    watt_list *= 8000 / 10

    data = [times_list, temp_list, cur_timestamp_list, watt_list]
    if extra_data:
        data = [times_list, temp_list, cur_timestamp_list, watt_list,cur_list,average_temp_list,power_transducer_list]

    return(data)

def update_plot(ax1,ax2,fig,new_data):
    """for ax in [ax1,ax2]:
        plt.sca(ax)"""
    plt.sca(ax1)
    plt.cla()
    plt.sca(ax2)
    plt.cla()
    if ax1.get_legend():
        ax1.get_legend.remove()
    #ax1.get_legend().remove()
    bundle_colors = ["Purples", "Reds", "Blues", "Greens", "Oranges"]
    for bundle_num in range(5):
        color_map = matplotlib.cm.get_cmap(bundle_colors[bundle_num])

        for couple_num in range(5):
            series_color = color_map((couple_num + 1) / 5)
            ax1.grid()
            ax1.plot(new_data[0], new_data[1][bundle_num][couple_num],
                     label=f"Bundle {bundle_num + 1} Couple {couple_num + 1}", color=series_color)
    ax2.plot(new_data[2],new_data[3])
    ax2.grid()

    plt.xlabel("Time (min)")

    box = ax1.get_position()
    ax1.set_position([box.x0, box.y0, box.width * 1, box.height])

    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.2))
    ax1.set_ylabel("Temperature (°C)")

    """ax2.set_ylabel("Current (mA)")"""

    ax2.set_ylabel("Power (W)")

    box2 = ax2.get_position()
    ax2.set_position([box2.x0, box2.y0, box2.width * 1, box2.height])
    #plt.draw()
    fig.canvas.draw()
    fig.canvas.flush_events()

def plot_accessory_plots():
    (times_list, temp_list, cur_timestamp_list, watt_list,cur_list,
     average_temp_list,power_transducer_list) = rescan_files(extra_data=True)

    # Plot results
    plt.figure(figsize=(10, 10))
    plt.plot(cur_timestamp_list, cur_list)
    plt.grid()
    plt.xlabel("Time (min)")
    plt.ylabel("Current (mA)")
    plt.title("SCR Control Signal")
    plt.show()

    plt.figure(figsize=(10, 10))
    plt.plot(cur_timestamp_list, power_transducer_list)
    plt.grid()
    plt.xlabel("Time (min)")
    plt.ylabel("Voltage (V)")
    plt.title("Watt Transducer Output")
    plt.show()

    plt.figure(figsize=(10, 10))
    plt.plot(cur_timestamp_list, watt_list)
    plt.grid()
    plt.xlabel("Time (min)")
    plt.ylabel("Power (W)")
    plt.title("Measured Heater Power")
    plt.show()

    plt.figure(figsize=(10, 10))
    plt.plot(times_list, average_temp_list, "bo")
    plt.ylabel("Temperature (deg C)")
    plt.xlabel("Time (min)")
    plt.xlim(0, times_list[-1])
    plt.grid()
    plt.title("Average Temperature")
    plt.show()

def main():

    dynamic_update = True
    data = rescan_files()


    if dynamic_update:
        ax1, ax2, fig = gen_twin_plot(data,dynamic=True)
        while True:
            data = rescan_files()
            update_plot(ax1,ax2,fig,data)
    ax1, ax2, fig = gen_twin_plot(data)
    plot_accessory_plots()


if __name__ == "__main__":
    main()
