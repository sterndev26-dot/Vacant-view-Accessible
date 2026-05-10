import serial
import time
import re

def send_command(cmd_str, port):
    # Sends a command string to the specified serial port with CRLF appended.
    # Waits 0.5 seconds after sending.
    port.write((cmd_str + '\r\n').encode())
    time.sleep(0.5) 

def read_response(timeout=3, port=None):
    # Reads data from the serial port for a specified timeout duration.
    # Returns the collected data decoded as a string.
    end_time = time.time() + timeout
    response = b''
    while time.time() < end_time:
        if port.in_waiting > 0:
            response += port.read(port.in_waiting)
        else:
            time.sleep(0.1)
    return response.decode(errors='ignore')

def get_mesh(port):
    # Sends a mesh network query command and returns the response as a string.
    string_data = '*AT+NODE_MSG,FFFF,@ST;##'
    send_command(string_data, port)
    resp = read_response(5, port)
    print(resp)  # Uncomment for debugging
    #port.close()  # Port is not closed here
    return str(resp)

def check_accessible_cubicles(*serial_list):
    # Checks accessibility of devices on given serial ports.
    # Returns a tuple (m_server, w_server), where 0 means accessible, 1 means not accessible.
    m_server, w_server = 1, 1
    
    for n_ports, s_port in enumerate(serial_list):
        resp = get_mesh(s_port)
        is_accessible = re.search(r'/*AS-', resp)
        if is_accessible and n_ports == 0:
            m_server = 0
        elif is_accessible and n_ports == 1:
            w_server = 0    
    return (m_server, w_server)

#check_accessible_cubicles(serial.Serial('/dev/ttyAMA4', 115200))
