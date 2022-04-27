#Author: Joshua Rampy
#Description: Server side of a socket program
#Version: 1.0

import sys
import random
import socket #For sockets
import logging #For debug and output
import struct #For unpacking packets


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

    #Iterating through command line arguments and assigning to variables
    ##DEBUG: Various debug logs to print variable assignments
    for i in range(1, len(sys.argv)):

        if sys.argv[i] == '-p':
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

    #Checking if port is in valid range
    if port > 0 and port < 65546:
        logger.debug('Valid port')
    else:
        logger.error('ERROR: Port is not valid. Out of range.')
        exit()

    #Creating socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.info('Socket created successfully')
    except socket.error as err:
        logger.error('Socket could not be created. Error: %s' %(err))
        exit()

    file_handler = logging.FileHandler(log_file)
    logger.addHandler(file_handler)

    s.bind(('', port))

    while True:

        s.listen(5)

        #Connecting then recieving data
        connection, address = s.accept()
        logger.info('Succesful connection from: %s' %(str(address)))

        while(True):
            header = connection.recv(12)
            version, msg_type, msg_len = struct.unpack('iii', header)
            logger.info(f'Header: {version}, {msg_type}, {msg_len}')
            
            if version != 17:
                logger.info('Version mismatch: Severing Connection')
                connection.close()
                break

            message_hex = connection.recv(10)
            message_tuple = struct.unpack(f'{str(msg_len)}s', message_hex)
            message = message_tuple[0].decode('utf-8')

            if msg_type == 1 or msg_type == 2:
                logger.info(f'Executing supported command: {message}')
                connection.send('SUCCESS'.encode('utf-8'))
            else:
                logger.info(f'Ignoring command: Unknown command - {msg_type}')
                
                if 'HELLO' in message:
                    logger.info('Recieved HELLO message: Responding')
                    connection.send('HELLO'.encode('utf-8'))

                if  'DISCONNECT' in message:
                    logger.info('Recieved DISCONNECT message: Severing connection')
                    connection.close()
                    break


    connection.close()
    s.close()



if __name__ == '__main__':
    main()