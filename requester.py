import socket
import argparse
import sys
import struct

# Packet types
REQUEST_PACKET = b'R'
DATA_PACKET = b'D'
END_PACKET = b'E'

# Header format
HEADER_FORMAT = '!cII'
BUFFER_SIZE = 4096

# Define the tracker filename
TRACKER = 'tracker.txt'


# Define a function to parse the tracker file
def parse_tracker_file():
    senders = {}
    with open(TRACKER, 'r') as f:
        for line in f:
            fields = line.strip().split()
            filename, seq_num, hostname, port = fields
            seq_num = int(seq_num)
            port = int(port)
            sender_key = (filename, seq_num)
            if sender_key not in senders:
                senders[sender_key] = []
            senders[sender_key].append((hostname, port))
    return senders


#  Takes in the necessary packet fields, constructs the packet, sends it to the specified
#  receiver, and waits for a response.
#  If the response payload is not empty, it is returned.
def send_request(filename, seq_num, payload, receiver_hostname, receiver_port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        packet_type = b'R'
        seq_num = socket.htonl(seq_num)
        length = 0
        payload = payload.encode()
        packet = struct.pack('!cII', packet_type, seq_num, length) + payload
        sock.sendto(packet, (receiver_hostname, receiver_port))
        data, server = sock.recvfrom(BUFFER_SIZE)
        response_type, response_seq_num, response_length = struct.unpack('!cII', data[:9])
        response_payload = data[9:]
        return response_payload


# Uses the parse_tracker_file function to read the tracker file and get a list of sender hostnames
# and ports for the specified file. Then sends a request packet to each sender in sequence,
# starting from sequence number 1. If a sender responds with a non-empty payload, it yields the
# payload to the calling code.
def request_file(filename):
    senders = parse_tracker_file()
    seq_num = 1
    payload = filename
    while True:
        sender_key = (filename, seq_num)
        if sender_key not in senders:
            break
        sender_list = senders[sender_key]
        for sender in sender_list:
            response = send_request(filename, seq_num, payload, sender[0], sender[1])
            if response:
                yield response
        seq_num += 1


# Command line argument
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", type=int,
                    help="port on which the requester waits for packets")
parser.add_argument("-o", "--file", type=str,
                    help="the name of the file that is being requested")
args = parser.parse_args()

# Process command line argument
sender_port = args.port
filename = args.file

# listen_port = args.port
listen_ip = '127.0.0.1'
listen_port = 12345

# create a UDP socket and bind it to the specified address and port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((listen_ip, listen_port))

# receive packets until an empty packet is received
packets = []
while True:
    packet, addr = sock.recvfrom(1024)
    if not packet:
        break
    packets.append(packet)

# write the received data to a file
with open('received_file.txt', 'wb') as f:
    data = b''.join(packets)
    f.write(data)

# print receipt information
print(f'Received {len(packets)} packets and wrote {len(data)} bytes to received_file.txt')

# close the socket
sock.close()
