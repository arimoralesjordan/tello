# Video Test

# Import the necessary modules
import socket
import threading
import time
import libh264decoder
import numpy as np
import pdb

# IP and port of Tello
tellos = [
  ('10.0.1.24', 8889)
]

# set the decoder
decoder = libh264decoder.H264Decoder()

# IP and port of local computer
local1_address = ('', 9010)
localv_address = ('', 11111)

# Create a UDP connection that we'll send the command to Tello(s)
socks=[]
for s in tellos:
  socks.append(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) 

videoSocks = []
for s in tellos:
  videoSocks.append(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))

# Bind to the local address and port
for i in range(len(socks)):
  socks[i].bind(local1_address)

# Binding Video Socks to the local address
for i in range(len(videoSocks)):
  videoSocks[i].bind(localv_address)

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
      print("Error receiving: " + str(e))
      break

# Create and start a listening thread that runs in the background
# This utilizes our receive functions and will continuously monitor for incoming messages
receiveThread = threading.Thread(target=receive)
receiveThread.daemon = True
receiveThread.start()

# Put Tello into command mode
send("command", 3)

# Send Stream on Command
send("streamon", 3)

def receive_video_thread():
  """
  Listens for video streaming (raw h264) from the Tello.
  Runs as a thread, sets self.frame to the most recent frame Tello captured.
  """
  packet_data = ""
  Retframe = None
  print("Waiting for Frame Response")
  while True:
    try:
      for i in range(len(videoSocks)):
        res_string, ip = videoSocks[i].recvfrom(2048)
        packet_data += res_string
      print("Frame data pack received")
      # end of frame
      if len(res_string) != 1460:
        for frame in h264_decode(packet_data):
          Retframe = frame
          packet_data = ""
    except socket.error as exc:
      print("Caught exception socket.error : %s" % exc)
  return Retframe

def h264_decode(packet_data):
  """
  decode raw h264 format data from Tello
  :param packet_data: raw h264 data array
  :return: a list of decoded frame
  """
  res_frame_list = []
  frames = decoder.decode(packet_data)
  for framedata in frames:
    (frame, w, h, ls) = framedata
    if frame is not None:
      # print 'frame size %i bytes, w %i, h %i, linesize %i' % (len(frame), w, h, ls)
      frame = np.fromstring(frame, dtype=np.ubyte, count=len(frame), sep='')
      frame = (frame.reshape((h, ls / 3, 3)))
      frame = frame[:, :w, :]
      res_frame_list.append(frame)
  return res_frame_list

# thread for receiving video
receiveVideoThread = threading.Thread(target=receive_video_thread)
receiveVideoThread.daemon = True
receiveVideoThread.start()

# keep script runing for 30 sec to keep sock open
print("Runing for 30 Sec to keep socks open")
time.sleep(30)