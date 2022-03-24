#Author: Joshua Rampy
#Description: Client side of a socket program
#Version: 1.0

import sys
import socket #For sockets
import logging #For debug and output
import struct #For building structs



#Creating logger and stream handler
logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(sys.stdout)

#Formatting stream handler
formatter = logging.Formatter('%(message)s')
stream_handler.setFormatter(formatter)

#Logger configuration
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)




def main():
    #DEBUG: Printing command line arguments
    logger.debug('Command line arguments: %s' %(sys.argv))

    packet = struct.Struct('4s 4s 4s 10s')
    version = '17'.encode('utf-8')
    default_command = '0'.encode('utf-8')

    #Iterating through command line arguments and assigning to variables
    ##DEBUG: Various debug logs to print variable assignments
    for i in range(1, len(sys.argv)):
        if sys.argv[i] == '-s':
            server_ip = sys.argv[i+1]
            logger.debug('Assigning server_ip: %s' %(server_ip))

        elif sys.argv[i] == '-p':
            port = sys.argv[i+1]
            logger.debug('Assigning port: %s' %(port))

            #Signing port to an integer
            try:
                port = int(port)
            except Exception as err:
                logger.error('Port could not be signed to integer. Error: %s' %(err))
                exit()

        elif sys.argv[i] == '-l':
            log_file = sys.argv[i+1]
            logger.debug('Assigning log_file: %s' %(log_file))

    #Checking if server_ip is a valid Ipv4 address
    if server_ip.count(".") == 3 and all(0 <= int(i) <= 255 for i in server_ip.split(".")):
        logger.debug('Server IP verified as a valid Ipv4 address')
    else:
        logger.error('ERROR: IP address is not a valid Ipv4 address')
        exit()

    #Checking if port is in valid range
    if port > 0 and port < 65546:
        logger.debug('Valid port')
    else:
        logger.error('ERROR: Port is not valid. Out of range.')
        exit()

    #File handler for logger
    file_handler = logging.FileHandler(log_file)
    logger.addHandler(file_handler)

    #Creating socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.info('Socket created successfully')
    except socket.error as err:
        logger.error('Socket could not be created. Error: %s' %(err))
        exit()

    #Lowering timeout time of socket from 120 to 10
    s.settimeout(10)   

    #Connecting to server
    try:
        s.connect((server_ip, port))
        logger.info('Succesfully connected to: %s' %(server_ip + ':' + str(port)))
        
    except Exception as err:
        logger.error('Failed to connect and/or send/recieve data. Error: %s' %(err))
        s.close()
        exit()

    #Creating HELLO packet
    hello_packet = packet.pack((version, default_command, '5', 'HELLO'.encode('utf-8')))

    #Sending HELLO packet
    try:
        s.sendall(hello_packet)
        logger.debug('Sent %s to the server' %('HELLO packet'))

    except Exception as err:
        logger.error('Failed to send HELLO packet. Error: %s' %(err))
        s.close()
        exit()

    #Recieving response from server
    try:
        response = s.recv(1024)
        logger.info('Response from server after HELLO packet: %s' %(response))

    except Exception as err:
        logger.error('Failed to recieve data. Error: %s' %(err))
        s.close()
        exit()

    #Checking if HELLO message was recieved and responded to
    if response != 'HELLO':
        s.close()
        exit()

    #Creating COMMAND packet
    logger.info('Choose a command to execute:')

    done = False
    while not done:
        logger.info('1. LIGHTON')
        logger.info('2. LIGHTOFF')
        command = input('Enter the corresponding number: ')

        if command == '1' or command == '2':
            done = True
        else:
            logger.info('Invalid selection, make sure you are entering a number response:')
    

    if command == 1:
        command_packet = packet.pack((version, command, '7'.encode('utf-8'), 'LIGHTON'.encode('utf-8')))
    if command == 2:
        command_packet = packet.pack((version, command, '8'.encode('utf-8'), 'LIGHTOFF'.encode('utf-8')))
    #Done creating COMMAND packet


    #Sending COMMAND packet
    try:
        s.sendall(command_packet)
        logger.debug('Sent %s to the server' %(command + ' command'))

    except Exception as err:
        logger.error('Failed to send COMMAND packet. Error: %s' %(err))
        s.close()
        exit()

    #Recieving response from server
    try:
        response = s.recv(1024)
        logger.info('Response from server after COMMAND packet: %s' %(response))

    except Exception as err:
        logger.error('Failed to recieve data. Error: %s' %(err))
        s.close()
        exit()

    #Creating DISCONNECT packet
    disconnect_packet = packet.pack((version, default_command, '10'.encode('utf-8'), 'DISCONNECT'.encode('utf-8')))

    #Sending DISCONNECT packet
    try:
        s.sendall(disconnect_packet)
        logger.debug('Sent %s to the server' %('DISCONNECT packet'))

        s.close()
    except Exception as err:
        logger.error('Failed to send DISCONNECT. Error: %s' %(err))
        s.close()
        exit()

    

if __name__ == '__main__':
    main()