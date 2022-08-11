from pyModbusTCP.server import ModbusServer
from pyModbusTCP.client import ModbusClient
import struct
import time
import numpy as np

def float_to_hex(f):
    return hex(struct.unpack('<I', struct.pack('<f', f))[0])

def float_to_word_list(val):
    hex_val = float_to_hex(val)
    return([int(hex_val[6:],base=16),int(hex_val[2:6],base=16)])

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    client = ModbusClient(host="129.63.151.167", port=502)

    ch_addr_map = list(range(28672,28680,2))

    mA_value = 8


    if mA_value <= 4.0:
        mA_value = 4.001
    mA_values = float_to_word_list((mA_value - 4)/16 * 100)
    client.write_multiple_registers(ch_addr_map[0],mA_values)

    reset = False
    if reset:
        mA_values = [0.001,0.001,0.001,0.001]
        for i in range(4):
            client.write_multiple_registers(ch_addr_map[i],float_to_word_list(mA_values[i]))

    """for i in np.linspace(0.1,99,1000):
        client.write_multiple_registers(ch_addr_map[0],float_to_word_list(i))
        time.sleep(1)"""


