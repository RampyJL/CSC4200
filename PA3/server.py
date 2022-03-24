#Author: Joshua Rampy
#Description: Server side of a socket program
#Version: 1.0

import sys
import random
import socket #For sockets
import logging #For debug and output



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

    tosend = ''
    quotes = open('quotes.txt').read().splitlines()
    to_send = bytes(random.choice(quotes), 'utf-8')

    s.bind(('', port))
    s.listen(5)

    while True:

        #Connecting then recieving data

        connection, address = s.accept()
        logger.info('Succesful connection from: %s' %(str(address)))

        message = connection.recv(1024)
        logger.info('Message from client: %s' %(message))


        if 'network' in message.decode('utf-8'):
            connection.sendall(to_send)
            logger.debug('Sent %s to the client' %(tosend))

    connection.close()
    s.close()



if __name__ == '__main__':
    main()