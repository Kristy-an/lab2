import socket
import argparse
import struct
import datetime
import sys

# Packet types
REQUEST_PACKET = b'R'
DATA_PACKET = b'D'
END_PACKET = b'E'

# Header format
HEADER_FORMAT = '!cII'
BUFFER_SIZE = 4096

# Define the tracker filename
TRACKER = 'tracker.txt'


def print_packet_type(time, response_type, senderip, senderport, response_seq_num, response_length, payload):
    if response_type == b'D':
        print("DATA Packet")
        print("recv time:        ", time)
        print("sender addr:      ", senderip, ":", senderport)
        print("sequence:         ", response_seq_num)
        print("length:           ", response_length)
        print("payload:          ", payload)
        print("\n")
    elif response_type == b'E':
        print("End Packet")
        print("recv time:        ", time)
        print("sender addr:      ", senderip, ":", senderport)
        print("sequence:         ", response_seq_num)
        print("length:           ", response_length)
        print("payload:          ", payload)
        print("\n")


def print_summary(addr, packets_num, data_bytes, duration_ms, sec):
    print("Summary")
    print("sender addr:              ", addr)
    print("Total Data packets:       ", packets_num)
    print("Total Data bytes:         ", data_bytes)
    try:
        print("Average packets/second:   ", packets_num/sec)
    except ZeroDivisionError:
        print("Average packets/second:   ", packets_num/(duration_ms/1000))
    print("Duration of the test:     ", duration_ms, " ms")
    print("\n")

def cal_milli_diff(time_s, time_end):
    time_diff_milli = (time_end.second-time_s.second)*1000 + \
                (time_end.microsecond-time_s.microsecond)/1000
    return time_diff_milli

def cal_second_diff(time_s, time_end):
    second_diff = (time_end.minute - time_s.minute) * 60 + \
                time_end.second - time_s.second
    return second_diff

# Define a function to parse the tracker file
# Return a dictionary with ascending id number
def parse_tracker_file():
    senders = {}
    with open(TRACKER, 'r') as f:
        for line in f:
            fields = line.strip().split()
            filename, id, hostname, port = fields
            id = int(id)
            port = int(port)
            sender_key = (filename, id)
            if sender_key not in senders:
                senders[sender_key] = []
            senders[sender_key].append((hostname, port))
            sorted_senders = sorted(senders.items(), key=lambda x: x[0][1])
            sorted_senders_dict = {key: value for key, value in sorted_senders}
    return sorted_senders_dict


if __name__ == '__main__':
    # Command line argument
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int,
                        help="port on which the requester waits for packets")
    parser.add_argument("-o", "--file", type=str,
                        help="the name of the file that is being requested")
    args = parser.parse_args()
    # Process command line argument
    port = args.port
    filename = args.file
    listen_port = args.port
    listen_ip = '127.0.0.1'

    # create a UDP socket and bind it to the specified address and port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((listen_ip, port))

    # create a new file for writing the payload data
    with open(filename, 'wb') as f:
        senders = parse_tracker_file()

        id = 1
        seq_num = 0
        payload = filename

        packet_type = b'R'
        length = len(payload)
        header = struct.pack(HEADER_FORMAT, packet_type, seq_num, length)
        packet = header + payload.encode()

        # receive data from each ports
        while True:
            key = (filename, id)
            id += 1
            try:
                ip, port = senders[key][0]
            except KeyError:
                break
            sock.sendto(packet, (ip, port))
            data_packet_count = 0
            file_len = 0
            duration = 0
            recv = True
            while True:
                # receive a UDP packet
                data, server = sock.recvfrom(BUFFER_SIZE)
                # Record the start time
                if recv:
                    start_time = datetime.datetime.now()
                    recv = False
                # Record normal packet time
                time = datetime.datetime.now()

                # Parsing package
                response_type, response_seq_num, response_length = struct.unpack('!cII', data[:9])
                response_payload = data[9:]
                file_len += response_length
                is_not_end = response_type != END_PACKET

                # Print information & write data to file
                if is_not_end:
                    print_packet_type(time, response_type, ip, port, response_seq_num, response_length,
                                      response_payload.decode()[:4])
                    f.write(response_payload)
                    data_packet_count += 1
                else:
                    print_packet_type(time, response_type, ip, port, response_seq_num, response_length,
                                      response_payload.decode()[:4])
                    end_time = time
                    duration_ms = cal_milli_diff(start_time, end_time)
                    duration_sec = cal_second_diff(start_time, end_time)
                    break
            print_summary(server, data_packet_count, file_len, duration_ms, duration_sec)
        f.close()
        sys.exit()
