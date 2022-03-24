#Author: Joshua Rampy
#Description: Client side of a socket program
#Version: 1.0

import sys
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

    #Taking user input and encoding with utf-8
    message = input('What message would you like to send to the server?: ').encode('utf-8')

    #Connecting then recieving data
    try:
        s.connect((server_ip, port))
        logger.info('Succesfully connected to: %s' %(server_ip + ':' + str(port)))
        
    except Exception as err:
        logger.error('Failed to connect and/or send/recieve data. Error: %s' %(err))
        s.close()
        exit()

    try:
        s.sendall(message)
        logger.debug('Sent %s to the server' %(message))

    except Exception as err:
        logger.error('Failed to send data. Error: %s' %(err))
        s.close()
        exit()

    try:
        response = s.recv(1024)
        logger.info('Response from server: %s' %(response))

        s.close()
    except Exception as err:
        logger.error('Failed to recieve data. Error: %s' %(err))
        s.close()
        exit()



if __name__ == '__main__':
    main()