from cryptography.fernet import Fernet
import os
import json
import hashlib

with open("key.txt", "rb") as file:
	key = Fernet(file.read())


class FileDir:
	def isDirectory(self):
		pass

	def changeUserPermission(self, val):
		pass

	def changeGroupPermission(self, val):
		pass

	def changeInternalPermission(self, val):
		pass


class Directory(FileDir):
	def __init__(self, name, owner, parent, path, encryptedPath):
		self.name = name
		#self.owner = json.dumps(owner.__dict__)
		self.owner = owner
		self.userPermission = True
		self.groupPermission = False
		self.internalPermission = False
		#self.parent = json.dumps(parent.__dict__)
		self.parent = parent
		self.encryptedName = key.encrypt(name.encode()).decode()
		self.fileList = []
		self.path = path + name + "/"
		if owner is None:  # home dir
			self.encryptedPath = name + "/"
			#self.path = self.getEncryptedName() + "/"
		else:
			self.encryptedPath = encryptedPath + self.getEncryptedName() + "/"


	def setName(self, name):
		self.name = name
		self.encryptedName = key.encrypt(name.encode()).decode()

	def getName(self):
		return self.name

	def getEncryptedName(self):
		return self.encryptedName

	def getEncryptedPath(self):
		return self.encryptedPath

	def getOwner(self):
		return self.owner

	def getPath(self):
		return self.path

	def getParent(self):
		return self.parent

	def setParent(self, parent):
		self.parent = parent

	def getUserPerm(self):
		return self.userPermission

	def getGroupPerm(self):
		return self.groupPermission

	def getInternalPerm(self):
		return self.internalPermission

	def isDirectory(self):
		return True

	def changeUserPermission(self, val):
		self.userPermission = val

	def changeGroupPermission(self, val):
		self.groupPermission = val

	def changeInternalPermission(self, val):
		self.internalPermission = val

	def createFile(self, name, owner):
		newFile = File(name, owner, self)
		self.fileList.append(newFile)
		with open(self.getEncryptedPath() + newFile.getEncryptedName() + ".txt", "w"):
			pass
		return newFile

	def rmFile(self, delFile):
		self.fileList.remove(delFile)
		if os.path.exists(self.getEncryptedPath() + delFile.getEncryptedName()):
			os.remove(self.getEncryptedPath() + delFile.getEncryptedName())
		return

	def createDir(self, name, owner):
		newDir = Directory(name, owner, self, self.path, self.encryptedPath)
		self.fileList.append(newDir)
		if not os.path.exists(self.encryptedPath + newDir.getEncryptedName()):
			os.mkdir(self.encryptedPath + newDir.getEncryptedName())
		return newDir

	def otherCreate(self, name, owner):
		aPath = self.getEncryptedPath()
		newDir = Directory(name, owner, self.name, aPath)
		self.fileList.append(newDir.getName())
		if not os.path.exists(self.getEncryptedPath() + newDir.getEncryptedName()):
			os.mkdir(self.getEncryptedPath() + newDir.getEncryptedName())
		return newDir

	def listFiles(self, user):
		out_arr = []
		for fileObj in self.fileList:
			fileOwner = fileObj.getOwner()
			userGroup = user.getGroup()
			ownerGroup = fileOwner.getGroup()
			fileGroupPerm = fileObj.getGroupPerm()
			fileIntPerm = fileObj.getInternalPerm()
			if fileOwner == user or (userGroup == ownerGroup and fileGroupPerm is True) or fileIntPerm is True:
				if fileObj.isDirectory() is True:
					out_arr.append("*" + fileObj.getName())
				else:
					out_arr.append(fileObj.getName())
			else:
				if fileObj.isDirectory() is True:
					out_arr.append("*" + fileObj.getEncryptedName())
				else:
					out_arr.append(fileObj.getEncryptedName())
		return out_arr

	def listEncryptFiles(self):
		out_arr = []
		for fileObj in self.fileList:
			if fileObj.isDirectory() is True:
				out_arr.append("*" + fileObj.getEncryptedName())
			else:
				out_arr.append(fileObj.getEncryptedName())
		return out_arr


class File(FileDir):
	def __init__(self, name, owner, parent):
		self.name = name
		self.owner = owner
		self.userPermission = True
		self.groupPermission = False
		self.internalPermission = False
		self.parent = parent
		self.encryptedName = key.encrypt(str(name).encode()).decode()
		self.message = ""
		self.encryptedMessage = ""
		self.hash = hashlib.sha256("".encode()).hexdigest()

	def setName(self, name):
		self.name = name
		self.encryptedName = key.encrypt(str(name).encode()).decode()

	def getName(self):
		return self.name

	def getHash(self):
		return self.hash

	def getMessage(self):
		return self.message

	def getEncryptMessage(self):
		return self.encryptedMessage

	def getEncryptedName(self):
		return self.encryptedName

	def getOwner(self):
		return self.owner

	def getParent(self):
		return self.parent

	def setParent(self, parent):
		self.parent = parent

	def getUserPerm(self):
		return self.userPermission

	def getGroupPerm(self):
		return self.groupPermission

	def getInternalPerm(self):
		return self.internalPermission

	def isDirectory(self):
		return False

	def changeUserPermission(self, val):
		self.userPermission = val

	def changeGroupPermission(self, val):
		self.groupPermission = val

	def changeInternalPermission(self, val):
		self.internalPermission = val

	def writeFile(self, content):
		self.message = content
		self.encryptedMessage = key.encrypt(content.encode()).decode()
		with open(self.parent.encryptedPath + self.encryptedName + ".txt", "w") as wFile:
			wFile.write(self.getEncryptMessage())

	def readFile(self):
		return self.message

	# maybe add check file method to check integrity. If hacker changes the txt, compare to message and check if error
