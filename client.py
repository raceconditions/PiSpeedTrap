import socket
import sys
import io
import struct
import numpy as np
import cv2
import time

# Create a TCP/IP socket
lic_ip = "192.168.100.120"

# Connect the socket to the port on the server given by the caller
server_address = (lic_ip, 10000)

def getLicensePlateImage(filePath):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(server_address)
        print('connecting to %s port %s' % server_address)
        message = 'P_1'
        print('Getting License Plate...')
        sock.sendall(bytes(message, 'UTF-8'))
    
        connection = sock.makefile('rb')
        try:
            while True:
                # Read the length of the image as a 32-bit unsigned int. If the
                # length is zero, quit the loop
                bytelength = sock.recv(struct.calcsize('<L'))
                if not bytelength:
                   continue
                image_len = struct.unpack('<L', bytelength)[0]
                if not image_len:
                    break
                # Construct a stream to hold the image data and read the image
                # data from the connection
                image_stream = io.BytesIO()
                image_stream.write(connection.read(image_len))
                print("Retrieved license plate image from stream...")
                # Rewind the stream, open it as an image with PIL and do some
                # processing on it
                image_stream.seek(0)
                data = np.fromstring(image_stream.getvalue(), dtype=np.uint8)
                # "Decode" the image from the array, preserving colour
                image = cv2.imdecode(data, 1)
                cv2.imwrite(filePath, image)
                print("Wrote license plate images to %s" % filePath)
                break
        finally:
            connection.close()
    
    finally:
        sock.close()

#getLicensePlateImage("/var/www/images/test.jpg")
