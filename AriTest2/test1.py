# This example script demonstrates how to use Python to fly Tello in a box mission
# This script is part of our course on Tello drone programming
# https://learn.droneblocks.io/p/tello-drone-programming-with-python/

# Import the necessary modules
import socket
import threading
import time

# IP and port of Tello
tellos = [
  ('10.0.1.24', 8889)
]

# IP and port of local computer
local1_address = ('', 9010)

# Create a UDP connection that we'll send the command to
socks=[]
for s in tellos:
  socks.append(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) 

# Bind to the local address and port
for i in range(len(socks)):
  socks[i].bind(local1_address)

# Send the message to Tello and allow for a delay in seconds
def send(message, delay):
  # Try to send the message otherwise print the exception
  try:
    for i in range(len(socks)):
      socks[i].sendto(message.encode(), tellos[i])
      print("Sending message: " + message + " to " + tellos[i][0])
  except Exception as e:
    print("Error sending: " + str(e) + " on " + tellos[i][0])

  # Delay for a user-defined period of time
  time.sleep(delay)

# Receive the message from Tello
def receive():
  # Continuously loop and listen for incoming messages
  while True:
    # Try to receive the message otherwise print the exception
    try:
      for s in socks:
        response, ip_address = s.recvfrom(128)
        print("Received message: from Tello: " + response.decode(encoding='utf-8'))
    except Exception as e:
      # If there's an error close the socket and break out of the loop
      s.close()
      #sock2.close()
      print("Error receiving: " + str(e))
      break

# Create and start a listening thread that runs in the background
# This utilizes our receive functions and will continuously monitor for incoming messages
receiveThread = threading.Thread(target=receive)
receiveThread.daemon = True
receiveThread.start()

# Each leg of the box will be 100 cm. Tello uses cm units by default.
box_leg_distance = 100

# Yaw 90 degrees
yaw_angle = 90

# Yaw clockwise (right)
yaw_direction = "cw"

# Put Tello into command mode
send("command", 3)

# Send the takeoff command
send("takeoff", 4)

# Fly forward
send("forward " + str(box_leg_distance), 4)

# Yaw right
send("cw " + str(yaw_angle*2), 4)

# Fly forward
send("forward " + str(box_leg_distance), 4)

# Yaw right
send("cw " + str(yaw_angle*2), 4)

# Land
send("land", 5)

# Battery
send("battery?", 5)

# Print message
print("Mission completed successfully!")

# Close the socket
for s in socks:
  s.close()