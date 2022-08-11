#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This program reads thermocouple data from the https server launched by PAC Control
It parses the thermocouple data and writes it to a file
It calculates a current value for a control signal (4-20 mA) to be sent to the power controller
It writes this current value to a text file and also sends it to a LabView VI through OPC-UA
This program should be launched after the LabView VI so that it can communicate with it through
OPC-UA

      Control Signal
                      -----------------   ethernet  -----------
             -------< | CLICK Controller |-------------| LabView |
             |        -----------------             -----------
             V                                            ^
Bldg      -------                             ------------|
outlet    | SCR |                             |
          -------                             |
             |                                |   OPC-UA (open platform communication unified arch.)
             |                                |   Elect. current value
             |                                |
          -------                 HTTPS       |
          |     |        -------          -----------------
          | MFF |------> Opto 22 ------> | Python Script |
          |     |          I/O           -----------------
          -------        -------

                    reads themocouples

 SCR controls the heat comming into the MFF.

'''

import time
import numpy as np
import requests  # http and https
from requests.auth import HTTPBasicAuth
from opcua import Client

def main():

    # HTTPS data for communication with Opto 22 IO module
    fname = "https://129.63.151.170/api/v1/device/strategy/ios/analogInputs"
    username = "Administrator"
    password = '"]$XA' + "'B7;=yp<E+;4;yJZdm~s3ukYpL@"

    # Local variables
    output_thermo_filename = "TempFile_Aug_11_2pm.txt"
    output_current_filename = "CurrentFile.txt"

    # Let the games begin
    https_session = requests.Session()
    https_session.auth=HTTPBasicAuth(username,password)

    # Set the current for heating the MFF (see diagram above)
    current = 0.001

    #Starts the OPC UA client
    client = Client("opc.tcp://UMASS-MJ66PR7:49600")

    try:
        client.connect()
        client.load_type_definitions() # load definition of server specific structures/extension objects

        # Client has a few methods to get proxy to UA nodes that should always be in address space such as
        # Root or Objects
        root = client.get_root_node()
        print("Root node is: ", root)
        objects = client.get_objects_node()
        print("Objects node is: ", objects)

        # Node objects have methods to read and write node attributes as well as browse or populate
        # address space
        print("Children of root are: ", root.get_children())
        current_node = client.get_node("ns=2;s=Current_in")

        while True:
            # Get request to opto https server
            response = https_session.get(fname,verify=False)
            thermocouple_dict_list = response.json()

            mff_temp = np.zeros(25) # 25 thermo-couples
            for i, couple in enumerate(thermocouple_dict_list):
                #print(couple['name'],couple['value'])
                mff_temp[i] = couple['value']

            #print("Average Temperature is",np.average(mff_temp[:20]),"deg C")
            average_temp = np.average(mff_temp[:20]) # inside thermo-couples
            ref_temp = mff_temp[-1] # bottom thermo-couple
            # Writes current to OPC-UA node
            current_node.set_value(current)

            fout = open(output_thermo_filename, 'a')

            fout.writelines(str(time.time_ns())+str(list(mff_temp))+"\n")
            fout.close()
            #Writes current to text file
            fout = open(output_current_filename,'w')
            fout.write(str(current))
            fout.close()

            current += 0.001

            print("*"*80)
            time.sleep(2)
    finally:
        client.disconnect()

if __name__ == '__main__':
    main()
