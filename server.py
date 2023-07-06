import socket
from cryptography.fernet import Fernet
import json
import user
import group
import FileDir
import os
import shutil
import hashlib

keyFile = open("key.txt", "r")
key = keyFile.read()
key = Fernet(key)
keyFile.close()

users = {}
groups = []
directories = []
files = []

homeDir = FileDir.Directory("home", None, None, "", "")
directories.append(homeDir)
if os.path.exists(homeDir.getName()):
	shutil.rmtree(homeDir.getName())
os.mkdir(homeDir.getName())
# print("This is the name of the home directory:")
# print(homeDir.getEncryptedName())
print("This is the home path:")
print(homeDir.getPath())


def helpCommand(conn):
	help_string = """Welcome to Cole and Stuart's Secure File System Version Alpha 1
	Command List:
	help
	ls
	pwd
	mkdir <directory name>
	cd <.. or directory name>
	chmod <file/dir> <permType> <0/1>
	touch <filename>
	cat <filename>
	rm <filename>
	echo <filename> <message>
	Enter 'quit' to exit the SFS"""
	conn.send(help_string.encode())
	return


def check_perms(filedir, user_check):
	fileOwner = filedir.getOwner()
	userGroup = user_check.getGroup()
	ownerGroup = fileOwner.getGroup()
	fileGroupPerm = filedir.getGroupPerm()
	fileIntPerm = filedir.getInternalPerm()
	if fileOwner == user_check or (userGroup == ownerGroup and fileGroupPerm is True) or fileIntPerm is True:
		return True
	else:
		return False


def lsCommand(conn, cur_dir, cur_user):
	out_str = ""
	# if cur_dir.getGroupPerm() is False and cur_dir.getInternalPerm() is False and cur_dir.getOwner() != cur_user:
	#	fileList = cur_dir.listFiles(cur_user)
	# else:
	#	fileList = cur_dir.listEncryptFiles()
	fileList = cur_dir.listFiles(cur_user)
	print(fileList)
	if not fileList:
		conn.send("No files or directories found".encode())
		return
	for file in fileList:
		out_str += file
		out_str += ", "
	conn.send(out_str[0:-2].encode())
	return


while True:
	print("Welcome to the server")
	print("Enter 0 to give admin commands")
	print("Enter 1 to connect to a client")
	print("Enter 2 to shut down the server")
	try:
		serverInput = int(input("Enter: "))
	except:
		print("Unrecognized Input")
		continue
	if serverInput == 0:
		# Admin Commands
		serverInput = input("Enter An Admin Command: ")
		argList = serverInput.split(" ")
		if argList[0] == "newUser" and len(argList) == 3:
			if users.get(argList[1]) != None:
				print("Username already taken")
				continue
			newUser = user.User(argList[1], argList[2], None)
			users[argList[1]] = newUser
			# directories.append(directories[0].otherCreate(argList[1], argList[1]))
			# newDir = FileDir.Directory(argList[1], newUser, directories[0], directories[0].getPath(), directories[0].getEncryptedPath())
			newDir = directories[0].createDir(argList[1], newUser)
			newDir.changeGroupPermission(True)
			directories.append(newDir)
			# os.mkdir(homeDir.getPath() + newDir.getEncryptedName())
			continue
		# userFile.close()
		elif argList[0] == "newGroup":
			newGroup = group.Group(argList[1], [])
			groups.append(newGroup)
			continue
		# groupFile.close()
		elif argList[0] == "deleteUser" and len(argList) == 2:
			# Delete a user
			continue
		elif argList[0] == "addToGroup" and len(argList) == 3:
			userToAdd = argList[1]
			groupToAddTo = argList[2]
			for group in groups:
				if group.name == groupToAddTo:
					group.addUser(users[userToAdd])
					users[userToAdd].setGroup(group)
			continue
		elif argList[0] == "printUsers":
			for u in users:
				print(u + " " + users[u].password)
			continue
		elif argList[0] == "printGroups":
			for y in groups:
				print(y.name)
			continue
		else:
			print("Command not valid")
			continue
	elif serverInput == 1:
		pass
	elif serverInput == 2:
		break
	else:
		continue

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print("Server Socket Made")
	s.bind(("", 49200))

	s.listen()

	authenticated = False

	while True:
		c, addr = s.accept()
		print("Connected to ", addr)
		c.send('Thank you for connecting, please enter your login info.'.encode())

		while True:
			# Authenticate

			received = c.recv(1024).decode()
			username, password = received.split(" ")
			if users[username] == None:
				print("There is no user with this username")
				c.send("No User".enode())
				continue
			if password != users[username].password:
				print("Incorrect Password")
				c.send("Incorrect".encode())
				continue
			if password == users[username].password:
				authenticated = True
				c.send("Authenticated".encode())
				break

		currentUser = users[username]
		currentDirectory = None
		for d in directories:
			if d.getName() == username and d.getParent().getPath() == "home/":
				currentDirectory = d

		corruptList = ""
		for d in directories:
			for aFile in d.fileList:
				if aFile.getOwner().getName() != username:
					break
				if aFile.isDirectory():
					break
				print("Checking " + aFile.getName())
				# checkHash = hashlib.sha256(aFile.readFile().encode()).hexdigest()
				checkFile = open(d.getEncryptedPath() + aFile.getEncryptedName() + ".txt", "r")
				# print(checkHash)
				# print(aFile.getHash())
				fileContents = checkFile.read()
				print(fileContents)
				proper = hashlib.sha256(aFile.getEncryptMessage().encode()).hexdigest()
				checkHash = hashlib.sha256(fileContents.encode()).hexdigest()
				if checkHash != proper:
					print("Corrupted")
					corruptList += aFile.getName() + ", "
		if corruptList:
			c.send(("Corrupted Files: " + corruptList[0:-2]).encode())
		else:
			c.send("No corrupt files".encode())

		while authenticated == True:
			print("Connected to Client")
			print("Awaiting Instruction")
			received = c.recv(1024).decode()
			print(received)
			if received == "quit":
				authenticated = False
				c.send("Thank you for using our SFS".encode())
				c.close()
				break
			if received == "help":
				helpCommand(c)
				continue
			if received == "ls":
				lsCommand(c, currentDirectory, users[username])
				continue
			if received == "pwd":
				print(currentDirectory.getPath())
				c.send(currentDirectory.getPath().encode())
				continue
			commandList = received.split(" ")
			if len(commandList) < 2:
				print("Unrecognized Command")
				c.send("Unrecognized Command".encode())
				continue
			elif commandList[0] == "touch":
				filename = commandList[1]
				if currentUser != currentDirectory.getOwner():
					c.send("Not allowed to create file".encode())
					continue
				for file in currentDirectory.fileList:
					if file.getName() == filename:
						c.send("File with same name exists".encode())
						continue
				currentDirectory.createFile(filename, currentUser)
				touch_msg = "text file named " + filename + " has been created"
				c.send(touch_msg.encode())
				continue
			elif commandList[0] == "rm":
				filename = commandList[1]
				if currentUser != currentDirectory.getOwner():
					c.send("Not allowed to delete file".encode())
					continue
				found = False
				for file in currentDirectory.fileList:
					if file.getName() == filename and file.isDirectory() is False:
						currentDirectory.rmFile(file)
						c.send("File deleted.".encode())
						found = True
				if found is not True:
					c.send("File not found.".encode())
				continue
			elif commandList[0] == "cat":
				filename = commandList[1]
				found = False
				for file in currentDirectory.fileList:
					if file.getName() == filename and file.isDirectory() is False:
						if check_perms(file, currentUser):
							if not file.readFile():
								c.send(("No characters in text file " + file.getName()).encode())
							else:
								c.send(file.readFile().encode())
							found = True
							break
						else:
							c.send("No reading permissions".encode())
							found = True
							break
				if not found:
					c.send("Filename not found in directory or trying to delete folder".encode())
				continue
			elif commandList[0] == "echo":
				filename = commandList[1]
				message = " ".join(commandList[2:])
				found = False
				for file in currentDirectory.fileList:
					if file.getName() == filename and file.isDirectory() is False:
						if check_perms(file, currentUser):
							file.writeFile(message)
							c.send(("Wrote message to file " + filename).encode())
							found = True
							break
						else:
							c.send("No writing permissions".encode())
							found = True
							break
				if not found:
					if currentUser != currentDirectory.getOwner():
						c.send("Not allowed to create file".encode())
						continue
					newFile = currentDirectory.createFile(filename, currentUser)
					newFile.writeFile(message)
					c.send(("Wrote message to file " + filename).encode())
					continue
				continue
			elif commandList[0] == "mkdir":
				print("This is the current directory path:")
				print(currentDirectory.getEncryptedPath())
				# newDir = FileDir.Directory(commandList[1], currentUser, currentDirectory, currentDirectory.getPath(), currentDirectory.getEncryptedPath())
				newDir = currentDirectory.createDir(commandList[1], currentUser)
				print("This is the new directory name:")
				print(newDir.getEncryptedName())
				# os.mkdir(currentDirectory.getEncryptedPath() + newDir.getEncryptedName())
				directories.append(newDir)
				c.send(("Created Directory: " + commandList[1]).encode())
				continue
			elif commandList[0] == "cd":
				print("We are going to change directories")
				if commandList[1] == "..":
					if currentDirectory.getParent() == None:
						print("Invalid Command")
						c.send("Invalid Command".encode())
						continue
					else:
						currentDirectory = currentDirectory.getParent()
						c.send(("Changed Directory: " + currentDirectory.getName()).encode())
						continue
				found = False
				for d in directories:
					if d.getName() == commandList[1]:
						print("First Level")
						if d.getParent() == None:
							# Home Case
							pass
						elif d.getParent().getName() == currentDirectory.getName():
							# The directory exists and has the correct parent
							# Now we check permissions
							if d.getInternalPerm():
								currentDirectory = d
								found = True
								break
							if d.getGroupPerm():
								# Check if the user is the owner
								if d.getOwner().getGroup() == currentUser.getGroup():
									print(d.getOwner().getGroup(), currentUser.getGroup())
									currentDirectory = d
									found = True
									break
							if d.getUserPerm():
								if d.getOwner().getName() == currentUser.getName():
									currentDirectory = d
									found = True
									break
							# currentDirectory = d
							break
					else:
						continue
				if found:
					c.send(("Changed Directory: " + currentDirectory.getName()).encode())
					print("Success")
				else:
					print("Insufficient Permissions")
					c.send("Could not change directory".encode())
			elif commandList[0] == "chmod":
				print("We are changing a file's permissions")
				found = False
				# add error check for argument number
				for file in currentDirectory.fileList:
					message = "File not found"
					if file.getName() == commandList[1]:
						# This is the directory we are looking for
						print("It is found")
						if file.getOwner().getName() != currentUser.getName():
							# print("You cannot do that")
							# c.send("You cannot do that".encode())
							# break
							message = "You cannot do that"
							print("You cannot do that")
							c.send(message.encode())
							break
						found = True
						message = ""
						if commandList[2] == "user":
							print("Changing user permission")
							if commandList[3] == "0":
								file.changeUserPermission(False)
								message = "Changed"
							elif commandList[3] == "1":
								file.changeUserPermission(True)
								message = "Changed"
							else:
								message = "Invalid"
						if commandList[2] == "group":
							print("Changing group permission")
							if commandList[3] == "0":
								file.changeGroupPermission(False)
								message = "Changed"
							elif commandList[3] == "1":
								file.changeGroupPermission(True)
								message = "Changed"
							else:
								message = "Invalid"
						if commandList[2] == "internal":
							print("Changing internal permission")
							if commandList[3] == "0":
								file.changeInternalPermission(False)
								message = "Changed"
							elif commandList[3] == "1":
								file.changeInternalPermission(True)
								message = "Changed"
							else:
								message = "Invalid"
						break
				c.send(message.encode())
				continue
			else:
				c.send("Invalid command.".encode())
