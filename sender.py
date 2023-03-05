import socket
import argparse
import sys

# Packet types
REQUEST_PACKET = b'R'
DATA_PACKET = b'D'
END_PACKET = b'E'

# Header format
HEADER_FORMAT = '!cII'

# Command line parameter
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", type=int,
                    help="port on which the sender waits for requests")
parser.add_argument("-g", "--req_port", type=int,
                    help="requester port: port on which the requester is waiting")
parser.add_argument("-r", "--rate",
                    help="rate: the number of packets to be sent per second")
parser.add_argument("-q", "--seq_no",
                    help="seq_no: The initial sequence of the packet exchange")
parser.add_argument("-l", "--length",
                    help="length: the length of the payload(in bytes) in the packets")
args = parser.parse_args()

# # Limitation of command line parameter
# if not (2049 < args.port < 65536):
#     print("Error: Port number should be in the range of 2049 to 65536")
#     sys.exit(1)
# if not (2049 < args.req_port < 65536):
#     print("Error: Requester port number should be in the range of 2049 to 65536")
#     sys.exit(1)


# specify the IP address and port number of the receiver
requester_ip = '127.0.0.1'
sender_port = args.port         # port our sender on and listening
requester_port = args.req_port  # port that our sender should send to
send_rate = args.rate
payload_length = args.length


# create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.bind((requester_ip, sender_port))



# read the file to send
with open('file_to_send.txt', 'rb') as f:
    data = f.read()

# split the data into packets
packet_size = 1024
packets = [data[i:i + packet_size] for i in range(0, len(data), packet_size)]

# send each packet to the receiver
for i, packet in enumerate(packets):
    sock.sendto(packet, (requester_ip, requester_port))
    print(f'Sent packet {i + 1}/{len(packets)}')

# send an empty packet to signal end of transmission
sock.sendto(b'', (requester_ip, requester_port))

# close the socket
sock.close()
