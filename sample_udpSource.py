import asyncio
import numpy as np
import socket

HOST = '127.0.0.1'
PORT = 9999
FREQUENCY = 0.5  # Frequency of the sinusoidal signal in Hz
SAMPLING_RATE = 100  # How many samples per second to send


async def send_sinusoidal_signal():
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)
    # loop = asyncio.get_running_loop()

    t = 0  # Time variable
    dt = 1.0 / SAMPLING_RATE  # Time step based on sampling rate

    try:
        while True:
            # Generate sinusoidal signal value
            signal_value = np.array([t, np.sin(2 * np.pi * FREQUENCY * t)])
            message = signal_value.tobytes()

            # Send the message
            sock.sendto(message, (HOST, PORT))

            # Increment time
            t += dt

            # Wait for next sample time
            await asyncio.sleep(dt)
    finally:
        sock.close()


async def send_file_signal():
    data = np.loadtxt("waveHistory_44081.csv", delimiter=",")
    nData = data.shape[0]
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)
    # loop = asyncio.get_running_loop()

    t = 0  # Time variable
    dt = 0.1  # Time step based on sampling rate
    count = 0
    try:
        while True:
            # Generate sinusoidal signal value
            signal_value = np.array([t, data[count, 1]])
            print(signal_value)
            message = signal_value.tobytes()

            # Send the message
            sock.sendto(message, (HOST, PORT))

            # Increment time
            t += dt

            # Increment count
            count += 1
            if count >= nData:
                count -= nData

            # Wait for next sample time
            await asyncio.sleep(dt)
    finally:
        sock.close()

# Entry point of the script
if __name__ == '__main__':
    asyncio.run(send_file_signal())
