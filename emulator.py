import socket
import argparse
import struct
import datetime
import time
import sys

HEADER_FORMAT = '!cHIHIHIcII'


def parse_static_table(filename, emulator_host, emulator_port):
    """ Parse the forwarding table file

    Given a emulator's hostname and port number, only store the data related with this emulator.

    :param filename: file name of forwarding table
    :param emulator_host: Given emulator's hostname
    :param emulator_port: Given emulator's port number

    :return: return the table dictionary containing only the information related to the specified
     emulator.
    """
    table = {}
    with open(filename) as file:
        for line in file:
            fields = line.strip().split()
            curr_emulator_host, curr_emulator_port = fields[0], fields[1]
            curr_emulator = (curr_emulator_host, int(curr_emulator_port))
            if curr_emulator != (emulator_host, emulator_port):
                continue
            dest_host, dest_port = fields[2], fields[3]
            destination = (dest_host, int(dest_port))
            next_host, next_port = fields[4], fields[5]
            next_hop = (next_host, int(next_port))
            delay = int(fields[6])
            loss_probability = int(fields[7])
            if curr_emulator not in table:
                table[curr_emulator] = {}
            table[curr_emulator][destination] = {'next_hop': next_hop, 'delay': delay,
                                                 'loss_probability': loss_probability}
    return table


def log(error_type, packet, logfile):
    """ Log the error information, write them to the log file

    :param error_type: type of the error
    :param packet: the dropped packet
    :param logfile: the file we need to write information in
    :return: None
    """
    pp, src_ip, src_port, dest_ip, dest_port, outer_len, ptype, pseq_num, plength \
        = struct.unpack(HEADER_FORMAT, packet[:26])
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    error_message = ""

    if error_type == "NOMATCH":
        error_message = "no forwarding entry found"
    elif error_type == "QFULL":
        error_message = "priority queue " + pp + "was full"
    elif error_type == "LOSS":
        error_message = "loss event occurred."

    with open(logfile) as file:
        file.write(error_message + ", ")
        file.write("Destination: " + dest_ip+" "+dest_ip + "， ")
        file.write("Source: " + src_ip + " " + src_port)
        file.write(", Time of loss: " + time)
        file.write(", Priority: " + pp + "payload size: " + plength)
        file.write("\n")
    return



# Command line parameter
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", type=int,
                    help="the port of the emulator")
parser.add_argument("-q", "--queue_size", type=int,
                    help="the size of each of the three queues.")
parser.add_argument("-f", "--filename", type=str,
                    help="The name of the file containing the static forwarding table")
parser.add_argument("-l", "--log", type=str,
                    help="The name of the log file")
args = parser.parse_args()

port = args.port
queue_size = args.queue_size
file_ft = args.filename
file_log = args.log

# create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
myIP = socket.gethostbyname(socket.gethostname())
sock.bind((myIP, port))

ftable = parse_static_table(file_ft, myIP, port)
print(ftable)
