fname = "thermo_data_log.txt"

with open(fname,'r') as file:
    data = file.readlines()

num_data_pts = int(len(data)/27)
time_list = []
point_list = []

for i in range(num_data_pts):
    timestamp = data[i*27]
    point = data[i*27+1:i*27+26]

    bundlenum_list = []
    couplenum_list = []
    #print(point)
    for entry in point:
        couple_full_name = entry.split(",")[0]
        bundlename,couplename= couple_full_name.split("_")
        bundlenum = bundlename.split("Bundle")[-1]
        couplenum = couplename.split("Couple")[-1]

        bundlenum_list.append(int(bundlenum))
        couplenum_list.append(int(couplenum))

    for bundle in range(5):
        for couple in range(5):
            if bundlenum_list[bundle*5 + couple] != bundle+1 or couplenum_list[bundle*5 + couple] != couple+1:
                print(timestamp,bundlenum_list[bundle*5 + couple],bundle,"|",couplenum_list[bundle*5 + couple],couple)

        #print(bundlenum,couplenum)
        #print(entry.split(",")[0])
    time_list.append(timestamp.strip("\n"))
    point_list.append(point)

#print(time_list,point_list)