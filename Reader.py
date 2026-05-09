# Creator = l3g0b0y

# ======================= #
# ====== IMPORTS ======== #
# ======================= #

try:
    import RPi.GPIO as gpio
    import serial
    import time
    from collections import deque
except ImportError as e:
    print("Import failure:\n", e)
    exit()

# ======================= #
# ===== GPIO SETUP ====== #
# ======================= #

gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

CASSETTE_DATA  = 18
CASSETTE_CLOCK = 23
STATUS_LED     = 24

gpio.setup(CASSETTE_DATA,  gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(CASSETTE_CLOCK, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(STATUS_LED,     gpio.OUT)

# ========================= #
# ===== SERIAL SETUP ====== #
# ========================= #

SERIAL_PORT = "/dev/serial0"
BAUD_RATE   = 9600

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# ========================= #
# ====== GLOBALS ========== #
# ========================= #

bit_buffer   = []
byte_queue   = deque()
reading_byte = False

# ========================= #
# ===== INTERRUPT ========= #
# ========================= #

def clock_interrupt(channel):
    global bit_buffer, reading_byte

    bit = gpio.input(CASSETTE_DATA)

    # ----------------------------- #
    # Detect START BIT (0)          #
    # ----------------------------- #
    if not reading_byte:
        if bit == 0:
            bit_buffer = []
            reading_byte = True
        return

    # ----------------------------- #
    # Read 8 DATA bits              #
    # ----------------------------- #
    if len(bit_buffer) < 8:
        bit_buffer.append(bit)
        return

    # ----------------------------- #
    # STOP BIT (should be 1)        #
    # ----------------------------- #
    if len(bit_buffer) == 8:
        if bit == 1:
            # Convert bits to byte
            value = 0
            for b in bit_buffer:
                value = (value << 1) | b

            byte_queue.append(value)

        # Reset state
        reading_byte = False
        bit_buffer = []

# ========================= #
# ====== SETUP IRQ ======== #
# ========================= #

gpio.add_event_detect(
    CASSETTE_CLOCK,
    gpio.RISING,
    callback=clock_interrupt,
    bouncetime=1   # debounce (adjust if needed)
)

# ========================= #
# ====== MAIN LOOP ======== #
# ========================= #

def main():
    print("Cassette reader (INTERRUPT MODE) started")

    try:
        gpio.output(STATUS_LED, 1)

        while True:

            if byte_queue:
                byte = byte_queue.popleft()

                # --- Debug --- #
                print(f"BYTE: {byte:08b}")

                # --- Serial Output --- #
                ser.write(bytes([byte]))

            else:
                # Idle sleep (low CPU usage)
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
