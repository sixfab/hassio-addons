import time
from serial.tools import list_ports
import json
import subprocess

config = {}

# Module support
supported = {
    "EG25-G": {
        "vendor": "quectel",
        "module": "EG25-G",
        "vid": "2c7c",
    },
}

# read bashio config
CONFIG_PATH = '/data/options.json'
with open(CONFIG_PATH) as json_file:
    config = json.load(json_file)

MODULE = config.get('module')
PORT = config.get('port')
APN = config.get('apn')
INTERVAL = config.get('interval')
DEBUG = config.get('debug')

MODULE_VENDOR = supported[MODULE]['vendor']
MODULE_VID = supported[MODULE]['vid']

if DEBUG:
    print("----------------------------------------")
    print(f"Module: {MODULE}")
    print(f"Port: {PORT}")
    print(f"APN: {APN}")
    print(f"Interval: {INTERVAL}")
    print(f"Module vendor: {MODULE_VENDOR}")
    print(f"Module vid: {MODULE_VID}")
    print("----------------------------------------")

def shell_command(command):
    try:
        com = command.split(" ")
        cp = subprocess.run(
            com, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except Exception as error:
        print("Message: %s", error)
        return {"stdout": "", "stderr": "", "returncode": 1}
    else:
        return {"stdout": cp.stdout, "stderr": cp.stderr, "returncode": cp.returncode}

def send_at_com(command, port, desired):
    try:
        cp = subprocess.run(
            ["atcom", command, "--port", port, "--find", desired],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except Exception as error:
        print("Message: %s", error)
        return {"stdout": "", "stderr": "", "returncode": 1}
    else:
        return {"stdout": cp.stdout, "stderr": cp.stderr, "returncode": cp.returncode}
        

def check_modem_exists():
    ports = list_ports.comports()
    for port in ports:
        for module in supported:
            if port.vid == int(supported[module]['vid'], 16):
                # print(f"Found modem with vid: {port.vid}")
                return True


def wait_for_modem(timeout=60):
    """Wait for modem exists or timeout"""
    end_of_timeot = time.time() + timeout
    while True:
        if check_modem_exists():
            print("Modem found")
            return True
        if time.time() > end_of_timeot:
            print("Modem couldn't be found")
            return False


def set_usb_mode():
    output = send_at_com(command="AT+QCFG=\"usbnet\",1", port=PORT, desired="OK")

    if output.get("returncode") == 0:
        print("USB mode set successfully. Rebooting modem...")
        return True


def check_usb_mode():
    desired_result = f'+QCFG: "usbnet",1'
    output = send_at_com(command="AT+QCFG=\"usbnet\"", port=PORT, desired=desired_result)
    
    if output.get("returncode") == 0:
        # print("USB mode is correct")
        return True
    else:
        print("USB mode is incorrect. Setting correct mode...")
        set_usb_mode()
        time.sleep(10) # wait for modem to turn off
        wait_for_modem()


def set_apn():
    output = send_at_com(command=f'AT+CGDCONT=1,"IPV4V6","{APN}"', port=PORT, desired="OK")
    if output.get("returncode") == 0:
        print("APN set successfully")
        return True


def check_apn():
    desired_result = f"+CGDCONT: 1,\"IPV4V6\",\"{APN}\""
    output = send_at_com(command="AT+CGDCONT?", port=PORT, desired=desired_result)

    if output.get("returncode") == 0:
        # print("APN is correct")
        return True
    else:
        print("APN is incorrect. Setting correct APN...")
        set_apn()


def main():
    if check_modem_exists():
        check_apn()
        check_usb_mode()
    else:
        print("Modem not found. Waiting for modem...")

main()