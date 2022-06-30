import numpy as np
from matplotlib import pyplot as plt
import shutil
import ast
import time
import math
import matplotlib
import datetime

#Reads thermocouple data from text file, copies it to a temporary file and then plots all of it
def convert_to_unixtimestamp(timestamp):
    """
    Takes timestamps in mm/dd/yyyy hh:mm:ss form and converts to unix timestamp
    """
    (date, inputTime) = timestamp.split(" ")

    (month, day, year) = date.split("/")
    (hour, minute, second) = inputTime.split(":")
    # print(month,day,year)
    date_time = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))

    unixTimestamp = time.mktime(date_time.timetuple())
    #print(unixTimestamp)
    return (unixTimestamp)

begin_time = time.time()

shutil.copy("TempFile_Jun13_120pm.txt","copiedTempFile.txt")
shutil.copy("CurrentFile_Jun13_120pm.txt","copiedCurrentFile.txt")
averageTemp_list = []
refTemp_list = []
timesList = []
tempList = [
    [[],[],[],[],[]],
    [[],[],[],[],[]],
    [[],[],[],[],[]],
    [[],[],[],[],[]],
    [[],[],[],[],[]]
]

cur_data = []
cur_list = []
power_transducer_list = []
cur_timestampList = []

with open("copiedTempfile.txt",'r') as f:
    for line in f.readlines():
        #data = f.readline()[19:]
        line_list = np.asarray(ast.literal_eval(line[19:]))
        timesList.append(line[:19])
        #print("a",timesList)
        averageTemp = np.average(line_list[:20])
        refTemp = line_list[-1]

        averageTemp_list.append(averageTemp)
        refTemp_list.append(refTemp)

        for coupleNum,coupleVal in enumerate(line_list):
            bundleNum = math.floor(coupleNum/5)
            #print(bundleNum,coupleNum)
            tempList[bundleNum][coupleNum-bundleNum*5].append(coupleVal)

        #print(line_list)

timesList = np.asarray(timesList,dtype=np.int64)
timesList = timesList / (1e9)
startTime = timesList[0]

print("Values greater than runtime are",timesList[timesList>timesList[-1]])
print("indices are",np.nonzero(timesList>timesList[-1]))
"""with open("copiedTempfile.txt", 'r') as f:
    for line in f.readlines()[:2]:
        timesList.append(line[:19])
        print(timesList)"""



"""for line in data:

    line_list = np.asarray(ast.literal_eval(line[19:]))"""
with open("copiedCurrentFile.txt",'r') as file:
    cur_data = file.readlines()

for line in cur_data:
    cur_list.append(float(line.split("\t")[0])*1000)
    #power_transducer_list.append(float(line.split("\t")[1])/ 10 * 8000)
    power_transducer_list.append(float(line.split("\t")[1]))
    timestamp = line.split("\t")[-1].strip()[:-3]
    am_or_pm = line[-3:-1]

    unixTimestamp = convert_to_unixtimestamp(timestamp)

    if am_or_pm == "PM" and line[-12:-10] != "12":
        unixTimestamp += 60*60*12

    cur_timestampList.append(unixTimestamp)

cur_timestampList = np.asarray(cur_timestampList)
curStartTime = cur_timestampList[0]
cur_time_after_temp_start = curStartTime - startTime

if cur_time_after_temp_start <0:
    temp_offset = -cur_time_after_temp_start
    cur_offset = 0
else:
    temp_offset = 0
    cur_offset = cur_time_after_temp_start
print(curStartTime,startTime)
timesList -= (timesList[0] - temp_offset)
cur_timestampList -= (curStartTime - cur_offset)
#cur_timestampList -= curStartTime
timesList = timesList / (60)
cur_timestampList = cur_timestampList / (60)
timesList -= timesList[0]
print("done, took",time.time()-begin_time,"seconds")

#plt.plot(cur_timestampList)
#plt.show()

fig = plt.figure(figsize=(10,10))
plt.plot(cur_timestampList,cur_list)
plt.grid()
plt.xlabel("Time (min)")
plt.ylabel("Current (mA)")
plt.title("SCR Control Signal")
plt.show()

fig = plt.figure(figsize=(10,10))
plt.plot(cur_timestampList,power_transducer_list)
plt.grid()
plt.xlabel("Time (min)")
plt.ylabel("Voltage (V)")
plt.title("Watt Transducer Output")
plt.show()

fig = plt.figure(figsize=(10,10))
watt_list = np.asarray(power_transducer_list)
watt_list *= 8000 / 10
plt.plot(cur_timestampList,watt_list)
plt.grid()
plt.xlabel("Time (min)")
plt.ylabel("Power (W)")
plt.title("Measured Heater Power")
plt.show()


fig = plt.figure(figsize=(10,10))
plt.plot(timesList,averageTemp_list,"bo")
plt.ylabel("Temperature (deg C)")
plt.xlabel("Time (min)")
plt.xlim(0,timesList[-1])
plt.grid()
plt.title("Average Temperature")
plt.show()

fig, (ax1,ax2) = plt.subplots(2,1,sharex=True)
#fig, ax1 = plt.subplots()
fig.set_size_inches(15,8)

ax1.set_title(f"MFF Thermocouple Data ")
bundleColors = ["Purples","Reds","Blues","Greens","Oranges"]
for bundleNum in range(5):
    colorMap = matplotlib.cm.get_cmap(bundleColors[bundleNum])

    for coupleNum in range(5):
        seriesColor = colorMap((coupleNum+1)/5)
        ax1.plot(timesList, tempList[bundleNum][coupleNum], label=f"Bundle {bundleNum+1} Couple {coupleNum + 1}",color=seriesColor)
plt.xlabel("Time (min)")
#plt.ylabel("Temperature (°C)")

box = ax1.get_position()
ax1.set_position([box.x0, box.y0, box.width * 0.8, box.height])

ax1.legend(loc='center left', bbox_to_anchor=(1,0.5))
ax1.set_ylabel("Temperature (°C)")
ax1.grid()

ax2.plot(cur_timestampList,cur_list)
box2 = ax2.get_position()
ax2.set_position([box2.x0, box2.y0, box2.width * 0.8, box2.height])
ax2.set_ylabel("Current (mA)")
ax2.grid()

plt.savefig(str(time.time()) + ".png",dpi=300)
plt.show()

