import json

class Group:

	def __init__(self, name, users):
		self.name = name
		self.users = users

	def getUsers(self):
		return self.users

	def addUser(self, newUser):
		if newUser in self.users:
			print(newUser + " is already in this group")
			return
		self.users.append(newUser)
		return

	def removeUser(self, target):
		if target in self.users:
			self.users.remove(target)
		else:
			print(target + " is not in this group")
		return

	def inGroup(self, target):
		if target in self.users:
			return True
		else:
			return False