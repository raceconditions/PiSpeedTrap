import socket
import sys
import io
import socket
import struct
import time
import picamera

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Bind the socket to the address given on the command line
server_name = socket.gethostname()
server_address = ('', 10000)
print('starting up on %s port %s' % server_address)
sock.bind(server_address)
sock.listen(1)

start_time = 0

def captureAndSendImage(connection):
    global start_time
    print("capturing image")
    try:
        stream = io.BytesIO()
        camera.capture(stream, 'jpeg')
        print("capture stream created after %s seconds" % (time.time() - start_time) )
        # Write the length of the capture to the stream and flush to
        # ensure it actually gets sent
        print("Stream is at: ", stream.tell())
        connection.write(struct.pack('<L', stream.tell()))
        connection.flush()
        print("sent stream length after %s seconds" % (time.time() - start_time))
        # Rewind the stream and send the image data over the wire
        stream.seek(0)
        connection.write(stream.read())
        print("stream transmission complete after %s seconds" % (time.time() - start_time) )
        # Reset the stream for the next capture
        stream.seek(0)
        stream.truncate()
        # Write a length of zero to the stream to signal we're done
        connection.write(struct.pack('<L', 0))
    finally:
        connection.close()

with picamera.PiCamera() as camera:
    #camera.resolution = (640, 480)
    #camera.resolution = (1640, 1232)
    camera.resolution = (3280, 2464)

    # Start a preview and let the camera warm up for 2 seconds
    camera.start_preview()
    time.sleep(2)

    while True:
        print('waiting for a connection')
        connection, client_address = sock.accept()
        start_time = time.time()
        try:
            print('client connected:', client_address)
            while True:
                data = connection.recv(4).decode("utf-8")
                #if not data:
                #    continue
                print('received "%s"' % data)
                command, times = data.split("_")
                if command == "P":
                    print("got command")
                    captureAndSendImage(connection.makefile('wb'))
                else:
                    print("breaking")
                    break
        except ConnectionResetError:
            continue
        except ValueError:
            continue
        finally:
            connection.close()

sock.close()
