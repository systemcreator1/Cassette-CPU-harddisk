# Creator = l3g0b0y

#-------------#
#--Variables--#
#-------------#

ToolsTrueUSB = False
ToolsTrueSound = False

import time
import sys
import os

ABORT_TIMEOUT = 15
ESC_DELAY = 3
last_action_time = time.time()

#-----------#
#--Modules--#
#-----------#

import keyboard as ink
from tkinter import filedialog as fd

try:
    import usb.core as Pens
    import sounddevice as Paper

    ToolsTrueUSB = True
    ToolsTrueSound = True

except ImportError as e:
    print(f"Uh Oh! It looks like the app can't start!\n {e}")
    ToolsTrueUSB = False
    ToolsTrueSound = False

#-------------#
#--Functions--#
#-------------#

def reset_timer():
    global last_action_time
    last_action_time = time.time()

def abort_countdown():
    print(f"\n[!] Abort triggered. Closing in {ESC_DELAY} seconds...")
    
    for i in range(ESC_DELAY, 0, -1):
        print(f"Exiting in {i}...")
        time.sleep(1)

    print("Force closing application...")

    try:
        ink.unhook_all()   # remove all keyboard hooks
    except:
        pass

    sys.stdout.flush()

    import os
    os._exit(0)

def Selector():
    devices = list(Pens.find(find_all=True, idProduct=0x01))

    if len(devices) == 0:
        print("No Audio devices detected")
        return False

    print("Select USB devices")
    for i, dev in enumerate(devices):
        print(f"{i+1} : {dev}")

    try:
        keys = int(input("Enter index ID of device : "))
        return devices[keys - 1]
    except:
        print("Invalid selection")
        return False

def Writer():
    Dev = Pens.find(find_all=True, idProduct = 0x01)
    Dev = list(Dev)

    if len(Dev) == 0:
        print("No device found")
        return

    device = Dev[0]
    device.set_configuration()

    File = fd.askopenfilename(
        title="Select script",
        filetypes=[("Custom computer scripts", "*.asm *.bin *.c *.cpp")]
    )

    if not File:
        print("No file selected")
        return

    try:
        with open(File, "rb") as f:
            data = f.read()
            device.write(1, data)  # endpoint 1 (example)
        print("Write successful")
    except Exception as e:
        print(f"Write failed: {e}")

def DriverSetup():
    devices = list(Pens.find(find_all=True, idProduct=0x08))

    if len(devices) == 0:
        print("No Storage devices detected")
        return False

    print("Select USB devices")
    for i, dev in enumerate(devices):
        print(f"{i+1} : {dev}")

    try:
        keys = int(input("Enter index ID of device : "))
        return devices[keys - 1]
    except:
        print("Invalid selection")
        return False

def Writer1():
    Dev = Pens.find(find_all=True, idProduct = 0x01)
    Dev = list(Dev)

    if len(Dev) == 0:
        print("No device found")
        return

    device = Dev[0]
    device.set_configuration()

    File = fd.askopenfilename(
        title="Select script",
        filetypes=[("Custom computer scripts", "*.asm *.bin *.c *.cpp")]
    )

    if not File:
        print("No file selected")
        return

    try:
        with open(File, "rb") as f:
            data = f.read()
            device.write(1, data)  # endpoint 1 (example)
        print("Write successful")
    except Exception as e:
        print(f"Write failed: {e}")

#-----------------------#
#--Inputs-and-controls--#
#-----------------------#

ink.add_hotkey("esc", abort_countdown)

print("Welcome to the cassette PC encoder!")
print("Would you like to - \n1. Flash Custom Cassette ROM\n2. Setup custom drivers\n3. Exit")

while True:
    # ⏱ Auto abort
    if time.time() - last_action_time > ABORT_TIMEOUT:
        print("\n[!] No activity detected. Auto exiting...")
        break

    if ink.is_pressed("1"):
        reset_timer()
        print("\n[1] Flash selected")

        dev = Selector()
        if dev:
            confirm = input("install? (y/n): ").lower()
            if confirm == "y":
                Writer()
            else:
                print("Aborted")
        else:
            print("No devices found")

        ink.wait("1")

    elif ink.is_pressed("2"):
        reset_timer()
        print("\n[2] Driver flash selected")
        dev = DriverSetup()
        if dev:
            confirm = input("install? (y/n): ").lower()
            if confirm == "y":
                Writer1()
            else:
                print("Aborted")
        else:
            print("No devices found")

        ink.wait("1")
    
    elif ink.is_pressed("3"):
        reset_timer()
        print("Exiting...")
        break
