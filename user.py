import json
import group

class User:

	def __init__(self, name, password, group):
		self.name = name
		self.password = password
		#self.group = json.dumps(group.__dict__)
		self.group = group

	def setGroup(self, newGroup):
		#self.group = json.dumps(newGroup.__dict__)
		self.group = newGroup

	def getGroup(self):
		#return group.Group(self.group["name"], self.group["users"])
		return self.group

	def getName(self):
		return self.name
