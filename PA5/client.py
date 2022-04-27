import socket
import sys
import getopt
import struct
import logging
import os

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
            lb_ip = sys.argv[i+1]
            logger.debug('Assigning server_ip: %s' %(lb_ip))

        elif sys.argv[i] == '-p':
            lb_port = sys.argv[i+1]
            logger.debug('Assigning port: %s' %(lb_port))

            #Signing port to an integer
            try:
                lb_port = int(lb_port)
            except Exception as err:
                logger.error('Port could not be signed to integer. Error: %s' %(err))
                exit()

        elif sys.argv[i] == '-l':
            log_file = sys.argv[i+1]
            logger.debug('Assigning log_file: %s' %(log_file))

        
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.info('Socket created successfully')
    except socket.error as err:
        logger.error('Socket could not be created. Error: %s' %(err))
        exit()

    s.settimeout(30) 

    try:
        s.connect((lb_ip, lb_port))
        logger.info('Connecting to: %s' %(lb_ip))
    except socket.error as err:
        logger.error("Failed to connect. Error: %s" %(err))
        exit()

    #Packet building
    ip_request = struct.pack('ii', 17, 1)
    disconnect_packet = struct.pack('ii', 17, 2)
    url_request = struct.pack('ii', 17, 3)

    #Sending ip_request packet
    try:
        s.sendall(ip_request)
        logger.debug('Sent %s to the loab_balancer' %('ip_request packet'))

    except Exception as err:
        logger.error('Failed to send ip_request packet. Error: %s' %(err))
        s.close()
        exit()

    #Recieving response from server
    try:
        server_ip = s.recv(1024).decode('utf-8')
        server_ip = server_ip.strip()
        logger.info('Response from load_balancer after ip_request packet: %s' %(server_ip))

    except Exception as err:
        logger.error('Failed to recieve data. Error: %s' %(err))
        s.close()
        exit()

    try:
        s.sendall(disconnect_packet)
        logger.debug('Sent %s to the load_balancer' %('disconnect packet'))

    except Exception as err:
        logger.error('Failed to send disconnect packet. Error: %s' %(err))
        s.close()
        exit()

    s.close()

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.info('Second socket created successfully')
    except socket.error as err:
        logger.error('Socket could not be created. Error: %s' %(err))
        exit()   

    try:
        s.connect((server_ip, lb_port))
        logger.info('Connecting to: %s' %(lb_ip))
    except socket.error as err:
        logger.error("Failed to connect. Error: %s" %(err))
        exit()

    try:
        s.sendall(url_request)
        logger.debug('Sent %s to the server' %('url_request packet'))

    except Exception as err:
        logger.error('Failed to send url_request packet. Error: %s' %(err))
        s.close()
        exit() 
        
    #Recieving response from server
    try:
        response = s.recv(10000)
        logger.info('Response from server successful')

    except Exception as err:
        logger.error('Failed to recieve data. Error: %s' %(err))
        s.close()
        exit()

    try:
        s.sendall(disconnect_packet)
        logger.debug('Sent %s to the server' %('disconnect packet'))

    except Exception as err:
        logger.error('Failed to send disconnect packet. Error: %s' %(err))
        s.close()
        exit()

    s.close()


if __name__ == "__main__":
    main()
