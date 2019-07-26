
from django.db import models


class Node(models.Model):
	class Meta:
		verbose_name_plural = "Nodes"
		db_table = "nodes"

	node_id = models.IntegerField(default=0, unique=True)
	node_ip = models.GenericIPAddressField(protocol="IPv4")

	location = models.CharField(max_length=50)

	hasTmp = models.BooleanField(default=False)
	hasHum = models.BooleanField(default=False)
	hasLgt = models.BooleanField(default=False)
	hasSnd = models.BooleanField(default=False)
	hasVlt = models.BooleanField(default=False)
	hasAmp = models.BooleanField(default=False)

	def __str__(self):
		return "Node" + str(self.node_id)

	def save(self, *args, **kwargs):
		self.location = self.location.title()

		super().save(*args, **kwargs)

	def getTmps(self):
		if self.hasTmp:
			entries = NodeReading.objects.filter(node=self)
			return [ { "x" : entry.timestamp.strftime("%Y-%m-%dT%H:%M") + "+00:00", "y" : entry.temperature } for entry in entries ]
		else:
			return None

	def getHums(self):
		if self.hasHum:
			entries = NodeReading.objects.filter(node=self)
			return [ { "x" : entry.timestamp.strftime("%Y-%m-%dT%H:%M") + "+00:00", "y" : entry.humidity } for entry in entries ]
		else:
			return None

	def getLgts(self):
		if self.hasLgt:
			entries = NodeReading.objects.filter(node=self)
			return [ { "x" : entry.timestamp.strftime("%Y-%m-%dT%H:%M") + "+00:00", "y" : entry.light } for entry in entries ]
		else:
			return None

	def getSnds(self):
		if self.hasSnd:
			entries = NodeReading.objects.filter(node=self)
			return [ { "x" : entry.timestamp.strftime("%Y-%m-%dT%H:%M") + "+00:00", "y" : entry.sound } for entry in entries ]
		else:
			return None

	def getVlts(self):
		if self.hasVlt:
			entries = NodeReading.objects.filter(node=self)
			return [ { "x" : entry.timestamp.strftime("%Y-%m-%dT%H:%M") + "+00:00", "y" : entry.voltage } for entry in entries ]
		else:
			return None

	def getAmps(self):
		if self.hasAmp:
			entries = NodeReading.objects.filter(node=self)
			return [ { "x" : entry.timestamp.strftime("%Y-%m-%dT%H:%M") + "+00:00", "y" : entry.current } for entry in entries ]
		else:
			return None


class NodeReading(models.Model):
	class Meta:
		verbose_name_plural = "Node Readings"
		db_table = "node_readings"

	timestamp = models.DateTimeField(auto_now_add=True)
	node = models.ForeignKey(Node, on_delete=models.CASCADE)

	temperature = models.IntegerField(default=0)
	humidity = models.IntegerField(default=0)
	light = models.IntegerField(default=0)
	sound = models.IntegerField(default=0)
	voltage = models.IntegerField(default=0)
	current = models.IntegerField(default=0)

	def __str__(self):
		return str(self.timestamp) + "-Node" + str(self.node.node_id)

	def save(self, *args, **kwargs):
		if not self.node.hasTmp:
			self.temperature = 0
		if not self.node.hasHum:
			self.humidity = 0
		if not self.node.hasLgt:
			self.light = 0
		if not self.node.hasSnd:
			self.sound = 0
		if not self.node.hasVlt:
			self.voltage = 0
		if not self.node.hasAmp:
			self.current = 0

		super().save(*args, **kwargs)
