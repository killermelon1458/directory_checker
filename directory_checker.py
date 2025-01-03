import os
import time
from pythonEmailNotify import *
from datetime import datetime
# Configuration
DIRECTORIES_FILE = "directories.txt"  # Path to the file containing directories to check
SLEEP_TIME_SECONDS =1   # Time to sleep between checks (in seconds)
DELIMITER = '|'   
emailSender = EmailSender(
    smtp_server="smtp.gmail.com",
    port=587,
    login=os.getenv("EMAIL_ADDRESS"),
    password=os.getenv("EMAIL_PASSWORD"),
    default_recipient=os.getenv("MAIN_EMAIL_ADDRESS"))

def read_directories(filepath, delimiter=DELIMITER):
    """
    Reads the directories from the file.
    Each line in the file should represent a directory path, optionally followed by a delimiter
    and a message or other data. We only need the directory path portion (before the delimiter).
    
    Returns a list of directory paths.
    """
    directories = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:  # Ignore empty lines
                    # Split only once so we don't accidentally split paths that might have the delimiter
                    parts = line.split(delimiter, 1)
                    directory_path = parts[0].strip()
                    directories.append(directory_path)
    return directories

def check_directories_exist(directories):
    """
    Checks whether all directories in the list exist.
    Returns a tuple (all_exist, missing_directories).
    - all_exist: True if all exist, False otherwise.
    - missing_directories: List of directories that don't exist.
    """
    missing_directories = []
    for directory in directories:
        if not os.path.exists(directory):
            missing_directories.append(directory)

    all_exist = len(missing_directories) == 0
    return all_exist, missing_directories

def main():
    print("Starting directory existence checker...")
    notified = False
    failure = False
    missing_num_temp = 0
    while True:
        # Read directories to check
        directories = read_directories(DIRECTORIES_FILE)

        # Check directories
        all_exist, missing_directories = check_directories_exist(directories)
        missing_num = len(missing_directories)
        # Print results
        if all_exist:
            if failure == True:
                emailSender.sendEmail("Drives connected","All Drives are currently connected")
                file = open("driveFailureLog.txt", 'a', encoding= 'utf-8')
                file.write("All Drives are currently connected\n")
            notified = False
            failure = False
        
            

        

        else:
            current_datetime = datetime.now()
            if os.path.exists("driveFailureLog.txt"):
                file = open("driveFailureLog.txt", 'a', encoding= 'utf-8')
            else:
                file = open("driveFailureLog.txt", 'a', encoding= 'utf-8')
            
            failure = True
            
        if missing_num > missing_num_temp:
            notified = False
        if failure and not notified:
            emailSender.sendEmail('Drive Not Detected', "{} of your drive(s) was not detected".format(missing_num))
            notified = True
            for missing_dir in missing_directories:
                file.write( missing_dir+ " did not connect.  " +str(current_datetime) +"\n")
        missing_num_temp = missing_num
        
        if 'file' in locals() and file and not file.closed:
            file.close()

                
        # Sleep before the next check
        time.sleep(SLEEP_TIME_SECONDS)

if __name__ == "__main__":
    main()
