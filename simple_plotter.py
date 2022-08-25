import numpy as np
from matplotlib import pyplot as plt
import shutil
import ast
import time
import math
import matplotlib
import datetime
import requests  # http and https
from requests.auth import HTTPBasicAuth

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
    (times_list, temp_list) = data[:]
    fig, ax1 = plt.subplots(1, 1)
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


    return(ax1,fig)

def rescan_files(fname,extra_data=False):
    # Copies data files to temporary files
    shutil.copy(fname, "copied_temp_file.txt")

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
    #start_time = times_list[0]

    # print("Values greater than runtime are", times_list[times_list > times_list[-1]])
    # print("indices are", np.nonzero(times_list > times_list[-1]))


    #print("Current File Start Time:", cur_timestamp_list[0])
    #print("Temperature File Start Time:", start_time)


    times_list = times_list / 60
    if len(times_list) >0:
        times_list -= times_list[0]

    data = [times_list, temp_list]
    if extra_data:
        data = [times_list, temp_list, average_temp_list]

    return(data)

def update_plot(ax1,fig,new_data):
    """for ax in [ax1,ax2]:
        plt.sca(ax)"""
    plt.sca(ax1)
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

    plt.xlabel("Time (min)")

    box = ax1.get_position()
    ax1.set_position([box.x0, box.y0, box.width * 1, box.height])

    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax1.set_ylabel("Temperature (°C)")

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

def gen_thermo_file():
    # HTTPS data for communication with Opto 22 IO module
    fname = "https://129.63.151.170/api/v1/device/strategy/ios/analogInputs"
    username = "Administrator"
    password = '"]$XA' + "'B7;=yp<E+;4;yJZdm~s3ukYpL@"

    # Local variables
    output_thermo_filename = "simplePlotter.txt"
    full_log_filename = "thermo_data_log.txt"

    open(output_thermo_filename,'w').close()
    open(full_log_filename,'w').close()

    # Let the games begin
    https_session = requests.Session()
    https_session.auth = HTTPBasicAuth(username, password)
    return(fname,output_thermo_filename,https_session,full_log_filename)

def update_thermo_file(fname,output_thermo_filename,https_session,full_log_filename):


    # Get request to opto https server
    response = https_session.get(fname, verify=False)
    thermocouple_dict_list = response.json()

    timestamp = str(time.time_ns())

    mff_temp = np.zeros(25)  # 25 thermo-couples
    with open(full_log_filename,"a") as file:
        file.writelines(timestamp+"\n")
        for i, couple in enumerate(thermocouple_dict_list):
            file.writelines(couple['name']+ "," +str(couple['value'])+"\n")
            mff_temp[i] = couple['value']
        file.writelines("\n")


    # print("Average Temperature is",np.average(mff_temp[:20]),"deg C")
    average_temp = np.average(mff_temp[:20])  # inside thermo-couples
    ref_temp = mff_temp[-1]  # bottom thermo-couple


    fout = open(output_thermo_filename, 'a')

    fout.writelines(timestamp + str(list(mff_temp)) + "\n")
    fout.close()

    print("*" * 80)
    time.sleep(0.25)


def main():

    dynamic_update = True
    #data = rescan_files()


    if dynamic_update:
        fname, output_thermo_filename, https_session, full_log_filename = gen_thermo_file()
        # time.sleep(2)
        data = rescan_files(output_thermo_filename)
        ax1,  fig = gen_twin_plot(data,dynamic=True)
        while True:
            update_thermo_file(fname,output_thermo_filename,https_session,full_log_filename)
            data = rescan_files(output_thermo_filename)
            update_plot(ax1,fig,data)

    else:
        data = rescan_files("Final_Backup_8_12_22_535pm\simplePlotter.txt")
        ax1,  fig = gen_twin_plot(data)
        plt.show()



if __name__ == "__main__":
    main()
