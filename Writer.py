# Creator = l3g0b0y

# ======================= #
# ====== IMPORTS ======== #
# ======================= #

try:
    import RPi.GPIO as gpio
    import serial
    import time
except ImportError as e:
    print("Import failure:\n", e)
    exit()

# ======================= #
# ===== GPIO SETUP ====== #
# ======================= #

gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

# --- Pin Definitions --- #
CASSETTE_DATA  = 18   # Data input from cassette
CASSETTE_CLOCK = 23   # Clock signal from cassette
STATUS_LED     = 24   # Status indicator LED

# --- Pin Configuration --- #
gpio.setup(CASSETTE_DATA,  gpio.IN,  pull_up_down=gpio.PUD_DOWN)
gpio.setup(CASSETTE_CLOCK, gpio.IN,  pull_up_down=gpio.PUD_DOWN)
gpio.setup(STATUS_LED,     gpio.OUT)

# ========================= #
# ===== SERIAL SETUP ====== #
# ========================= #

SERIAL_PORT = "/dev/serial0"
BAUD_RATE   = 9600

ser = serial.Serial(
    port=SERIAL_PORT,
    baudrate=BAUD_RATE,
    timeout=1
)

# ========================= #
# ====== FUNCTIONS ======== #
# ========================= #

def wait_clock():
    """
    Wait for one full clock pulse (rising + falling edge)
    """

    # Wait for rising edge
    while gpio.input(CASSETTE_CLOCK) == 0:
        pass

    # Wait for falling edge
    while gpio.input(CASSETTE_CLOCK) == 1:
        pass


def read_byte():
    """
    Read 8 bits from DATA line synchronized with CLOCK
    Returns:
        int: byte value (0–255)
    """

    value = 0

    for _ in range(8):
        wait_clock()
        bit = gpio.input(CASSETTE_DATA)
        value = (value << 1) | bit

    return value


# ========================= #
# ====== MAIN LOOP ======== #
# ========================= #

def main():
    print("Cassette reader started")

    try:
        gpio.output(STATUS_LED, 1)

        while True:
            byte = read_byte()

            # --- Debug Output --- #
            print(f"BYTE: {byte:08b}")

            # --- Send via Serial --- #
            ser.write(bytes([byte]))

            # Small delay to avoid flooding
            time.sleep(0.001)

    except KeyboardInterrupt:
        print("\nStopping...")

    finally:
        gpio.output(STATUS_LED, 0)
        ser.close()
        gpio.cleanup()


# ========================= #
# ===== ENTRY POINT ======= #
# ========================= #

if __name__ == "__main__":
    main()
