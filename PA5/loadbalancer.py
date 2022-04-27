import socket
import sys
import getopt
import struct
import logging
import os
import time
import threading
from pythonping import ping

#Creating logger and stream handler
logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(sys.stdout)

#Formatting stream handler
formatter = logging.Formatter('%(message)s')
stream_handler.setFormatter(formatter)

#Logger configuration
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

#List of all servers with their pref
server_dict = dict()

def ping_servers(servers):
    while(True):
        for server in servers:
            ping_request = ping(target=server, count=10, timeout=2)
            logger.debug('Pinging server: %s' %(server))
            server_dict[server] = (0.75 * ping_request.packet_loss + 0.25 * ping_request.rtt_avg_ms)
        
        logger.info('Server preferences updated')
        time.sleep(60)

def get_best_server():
    return min(server_dict, key=server_dict.get)

def main():
    #DEBUG: Printing command line arguments
    logger.debug('Command line arguments: %s' %(sys.argv))

    #Iterating through command line arguments and assigning to variables
    ##DEBUG: Various debug logs to print variable assignments
    for i in range(1, len(sys.argv)):
        if sys.argv[i] == '-s':
            server_txt = sys.argv[i+1]
            logger.debug('Assigning server_txt: %s' %(server_txt))

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

    with open(server_txt) as f:
        servers = f.readlines()

    x = threading.Thread(target=ping_servers, args=(servers,), daemon=True)
    x.start()

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
            header = connection.recv(8)
            version, msg_type = struct.unpack('ii', header)
            logger.info(f'Header: {version}, {msg_type}')
            
            if version != 17:
                logger.info('Version mismatch: Severing Connection')
                connection.close()
                break
            
            if msg_type == 1:
                logger.info('Recieved ip request command')
                logger.info('Sending best server')
                connection.send(get_best_server().encode('utf-8'))
            elif msg_type == 2:
                logger.info('Recieved disconnect command')
                logger.info('Closing connection')
                connection.close()
                break
            else:
                logger.info('Recieved unknown command')
                logger.info('Severing connection')
                connection.close()
                break

    connection.close()
    s.close()

if __name__ == '__main__':
    main()