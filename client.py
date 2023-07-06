import socket

# Connect to the server
s = socket.socket()

s.connect(("10.2.4.152", 49200))
# print("Server Connected")
print(s.recv(1024).decode())

authenticated = False
while True:
	username = input("Enter Username: ")
	password = input("Enter Password: ")
	full = username + " " + password

	# Send to server
	s.send(full.encode())
	received = s.recv(1024).decode()
	print(received)
	if received == "Authenticated":
		authenticated = True

	if not authenticated:
		print("Failed to authenticate")
	else:
		print("Success")
		break



# Connected to server

#s.send("This is a command".encode())

#print(s.recv(1024).decode())
if not authenticated:
	quit()
print(s.recv(1024).decode())
while True:
	# Set path
	command = input("$ ")
	s.send(command.encode())
	if command == "quit":
		# Begin preparing to disconnect
		print(s.recv(1024).decode())
		s.close()
		break
	else:
		print(s.recv(1024).decode())
		continue
	# elif command == "help":
	# 	print(s.recv(1024).decode())
	# 	continue
	# elif command == "pwd":
	# 	print(s.recv(1024).decode())
	# 	continue
	# elif command == "ls":
	# 	print(s.recv(1024).decode())
	# 	continue
	# elif command.split()[0] == "mkdir":
	# 	print(s.recv(1024).decode())
	# 	continue
	# elif command.split()[0] == "cd":
	# 	print(s.recv(1024).decode())
	# 	continue
	# elif command.split()[0] == "chmod":
	# 	print(s.recv(1024).decode())
	# 	continue
	# elif command.split()[0] == "touch":
	# 	print(s.recv(1024).decode())
	# 	continue
	# elif command.split()[0] == "cat":
	# 	print(s.recv(1024).decode())
	# 	continue
	# elif command.split()[0] == "echo":
	# 	print(s.recv(1024).decode())
	# 	continue
	# elif command.split()[0] == "rm":
	# 	print(s.recv(1024).decode())
	# 	continue
