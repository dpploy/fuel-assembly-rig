from pyModbusTCP.server import ModbusServer
from pyModbusTCP.client import ModbusClient
import struct
import time
import numpy as np
import requests  # http and https
from requests.auth import HTTPBasicAuth

#Initialize PLC data register addresses
BIT_SP_LOWER_LIMIT_ENABLE = 16384
BIT_SP_UPPER_LIMIT_ENABLE = 16385

INT_PID_ENABLE = 17
INT_SAMPLE_RATE_MS = 5

FLOAT_SP_VALUE = 28680
FLOAT_SP_LOWER_LIMIT = 28682
FLOAT_SP_UPPER_LIMIT = 28684
FLOAT_PID_BIAS = 28688
FLOAT_PID_P = 28690
FLOAT_PID_I = 28692
FLOAT_PID_D = 28694
FLOAT_OUTPUT_LOWER_LIMIT = 28698
FLOAT_OUTPUT_UPPER_LIMIT = 28700
FLOAT_RAW_PV = 28702
#FLOAT_PV_VALUE = 28704
FLOAT_PV_VALUE = 28730
FLOAT_PV_LOWER_LIMIT = 28724
FLOAT_PV_UPPER_LIMIT = 28726

air_1 = False
air_2 = False
water_1 = True
if air_1:
    P_VAL = 7.06569
    I_VAL = 35.3099     #sec
    D_VAL = 5.88499     #sec
    SAMPLE_RATE_MS_VAL = 823    #msec

elif air_2:
    P_VAL = 6.0375471
    I_VAL = 23.82
    D_VAL = 3.97
    SAMPLE_RATE_MS_VAL = 555

elif water_1:
    P_VAL = 3.9317117
    I_VAL = 27.120001
    D_VAL = 4.52
    SAMPLE_RATE_MS_VAL = 632

def float_to_hex(f):
    return hex(struct.unpack('<I', struct.pack('<f', f))[0])

def float_to_word_list(val):
    if val == 0:
        return([0,0])
    hex_val = float_to_hex(val)
    return([int(hex_val[6:],base=16),int(hex_val[2:6],base=16)])

def write_float_value(client,address,value):
    val_word_list = float_to_word_list(value)
    client.write_multiple_registers(address, val_word_list)
    return

def change_setpoint(client,val):
    write_float_value(client,FLOAT_SP_VALUE,val)

def enable_pid(cilent):
    client.write_single_register(INT_PID_ENABLE,1)
    client.write_single_register(INT_PID_ENABLE-1, 1)

    write_float_value(client,FLOAT_PID_P,P_VAL)
    write_float_value(client, FLOAT_PID_I, I_VAL)
    write_float_value(client, FLOAT_PID_D, D_VAL)

    client.write_single_register(INT_SAMPLE_RATE_MS,SAMPLE_RATE_MS_VAL)

def disable_pid(client):
    client.write_single_register(INT_PID_ENABLE,0)
    client.write_single_register(INT_PID_ENABLE-1, 1)

def write_pv_value(client,val):
    write_float_value(client, FLOAT_RAW_PV, val)
    write_float_value(client, FLOAT_PV_VALUE,val)

def get_avg_temp():
    fname = "https://129.63.151.170/api/v1/device/strategy/ios/analogInputs"
    username = "Administrator"
    password = '"]$XA' + "'B7;=yp<E+;4;yJZdm~s3ukYpL@"

    # Let the games begin
    https_session = requests.Session()
    https_session.auth = HTTPBasicAuth(username, password)

    # Get request to opto https server
    response = https_session.get(fname, verify=False)
    thermocouple_dict_list = response.json()

    timestamp = str(time.time_ns())

    mff_temp = np.zeros(25)  # 25 thermo-couples

    for i, couple in enumerate(thermocouple_dict_list):
        mff_temp[i] = couple['value']
    average_temp = np.average(mff_temp[:10])  # inside heated thermo-couples

    return(average_temp)



if __name__ == '__main__':
    client = ModbusClient(host="129.63.151.167", port=502)

    ch_addr_map = list(range(28672,28680,2))
    print(ch_addr_map)


    #time.sleep(1)


    pid_loop = False
    if pid_loop:
        enable_pid(client)
        change_setpoint(client, 0.0)
        while True:
            average_temp = float(get_avg_temp())
            write_pv_value(client, average_temp)

    disable_pid(client)
    heater_mA = 4
    #VFD signal is in terms of % of 1800 RPM
    #   Ex: 10 mA corresponds to 675 RPM
    #       (10-4)/16 * 1800 = 675
    vfd_rpm = 0

    vfd_mA = vfd_rpm * 16 / 1800 + 4

    mA_list = [heater_mA,vfd_mA,4.0,4.0]

    for channel,mA_value in enumerate(mA_list):
        if mA_value <= 4.0:
            mA_value = 4.00
        mA_values = float_to_word_list((mA_value - 4)/16 * 100)
        client.write_multiple_registers(ch_addr_map[channel],mA_values)

    reset = False
    if reset:
        mA_values = [0,0,0,0]
        for i in range(4):
            client.write_multiple_registers(ch_addr_map[i],float_to_word_list(mA_values[i]))

    while True:
        average_temp = float(get_avg_temp())
        write_pv_value(client, average_temp)
    """for i in np.linspace(0.1,99,1000):
        client.write_multiple_registers(ch_addr_map[0],float_to_word_list(i))
        time.sleep(1)"""


