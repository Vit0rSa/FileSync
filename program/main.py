#############################################################################
#     Author:   Vítor Sá
#       Date:   09/05/2024
#Description:   program that synchronizes two folders: source and 
#               replica maintaining a full, identical copy of source folder 
#               at replica folder.
#Code Research: https://docs.python.org/3/howto/logging.html
#               https://www.studytonight.com/python/python-logging-in-file
#               https://www.geeksforgeeks.org/how-to-use-sys-argv-in-python/
#               https://www.geeksforgeeks.org/python-os-path-getmtime-method/
#############################################################################

import os
import sys
import time
import logging
import shutil

#Synchronizes the two folders
def sync_folders(source, replica, logger):
    #Insert into log file
    logger.info("Starting File Sync")

    #Run source_folder_exists    
    source_folder_exists(source, logger)
    #Run replica_folder_exists
    replica_folder_exists(replica, logger)

    #Get all files from source and replica
    source_items = set(os.listdir(source))
    replica_items = set(os.listdir(replica))

    #Checks what items need to be copied from source to replica
    items_to_copy = source_items - replica_items

    #Checks what items need to be removed from replica
    items_to_remove = replica_items - source_items

    #Check what items need to be updated
    items_to_update = source_items.intersection(replica_items)

    # print(items_to_copy)      #test commands
    # print(items_to_remove)    #test commands
    # print(items_to_remove)    #test commands

    #Function to copy either files or directories
    for item in items_to_copy:
        source_path = os.path.join(source, item)
        replica_path = os.path.join(replica, item)
        
        #Function adapted from https://pynative.com/python-copy-files-and-directories/
        if os.path.isdir(source_path):
            shutil.copytree(source_path, replica_path)
            #Insert into log file
            logger.info("Copied directory tree")
        else:
            shutil.copy2(source_path, replica_path)
            #Insert into log file
            logger.info("Copied file")
            
    #Function to update files
    for item in items_to_update:
        source_path = os.path.join(source, item)
        replica_path = os.path.join(replica, item)

        #Check if it is a directory, if so ignore
        if os.path.isdir(source_path):
            #Ignore
            continue
        
        source_mtime = os.path.getmtime(source_path)
        replica_mtime = os.path.getmtime(replica_path)

        #If file in source is newer then update in replica
        if source_mtime > replica_mtime:
            shutil.copy2(source_path, replica_path)
            #Insert into log file
            logger.info("Updated file")

    #Function to remove files from replica
    #Adapted from https://sentry.io/answers/delete-a-file-or-folder-in-python/
    for item in items_to_remove:
        item_path = os.path.join(replica, item)
        
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
            #Insert into log file
            logger.info("Removed directive tree")
        else:
            os.remove(item_path)
            #Insert into log file
            logger.info("Removed file")
    
    logger.info("File Sync finished")

#Checks if the source path exists and if not prints error
def source_folder_exists(source, logger):
    if not os.path.exists(source):
        #print("ERROR - source path does not exist") #test command
        #insert error into log file
        logger.error("source path does not exist")

#Checks if the replica path exists and if not creates it
def replica_folder_exists(replica, logger):
    if not os.path.exists(replica):
        #insert into log file
        #print("WARNING - replica path does not exist") #test command
        logger.warning("replica path does not exist")
        #creates path
        os.makedirs(replica)
        #print("ACTION - replica path created") #test command
        #insert into log file
        logger.info("replica path created")

#Setup for logger
def setup_logger(log_path):
    logger = logging.getLogger(log_path)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')

    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

def main():
    #Verify arguments from command
    if len(sys.argv) != 5:
        print('Usage: main.py <source_path> <replica_path> <log_file> <interval_in_seconds>')
        return

    #Get arguments from command
    source = sys.argv[1]
    replica = sys.argv[2]
    log_file = sys.argv[3]
    sync_interval = float(sys.argv[4])

    #Call Setup logger
    logger = setup_logger(log_file)

    #Run periodical Sync until user intervention
    try:
        while True:
            sync_folders(source, replica, logger)
            logger.info(f'sleeping for {sync_interval} seconds...')
            #sleep for given seconds (interval)
            time.sleep(sync_interval)
    except KeyboardInterrupt:
        logger.info("Sync stoped: user intervention")

if __name__ == "__main__":
    main()