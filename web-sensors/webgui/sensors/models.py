
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

	def jsCharts(self, depth=None, period=None):
		return NodeReading.jsCharts(node=self, depth=depth, period=period)


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

	@property
	def js_timestamp(self):
		return self.timestamp.strftime("%Y-%m-%dT%H:%M")

	@classmethod
	def searchNode(cls, node, depth=None, period=None):
		array = cls.objects.filter(node=node).order_by('-timestamp')
		
		if not depth == None:
			return array[:depth]
		
		elif not period == None:
			if period[0] > period[1]:
				raise ValueError("Reading Search : Start time more recent than End time.")

			start_idx = None
			end_idx = None
			
			for idx,entry in enumerate(array):
				if entry.timestamp <= period[1]:
					start_idx = idx
					break
			if not start_idx == None:
				for idx,entry in enumerate(array[start_idx:]):
					if entry.timestamp <= period[0]:
						end_idx = start_idx + idx
						break
			else:
				return []

			if end_idx == None:
				end_idx == len(array) - 1

			return array[start_idx:end_idx]
		
		else:
			return array

	@classmethod
	def jsCharts(cls, node, depth=None, period=None):
		db = cls.searchNode(node=node, depth=depth, period=period)

		tmp_set = []
		hum_set = []
		lgt_set = []
		snd_set = []
		vlt_set = []
		amp_set = []

		for entry in db:
			tmp_set.append( { "t" : entry.js_timestamp, "y" : entry.temperature } )
			hum_set.append( { "t" : entry.js_timestamp, "y" : entry.humidity } )
			lgt_set.append( { "t" : entry.js_timestamp, "y" : entry.light } )
			snd_set.append( { "t" : entry.js_timestamp, "y" : entry.sound } )
			vlt_set.append( { "t" : entry.js_timestamp, "y" : entry.voltage } )
			amp_set.append( { "t" : entry.js_timestamp, "y" : entry.current } )

		charts = []
		if node.hasTmp:		charts.append({ "name" : "Temperature",	"color" : [255,	153,51],	"set" : tmp_set })
		if node.hasHum:		charts.append({ "name" : "Humidity",	"color" : [0,	0,	255],	"set" : hum_set })
		if node.hasLgt:		charts.append({ "name" : "Light",		"color" : [255,	255,51],	"set" : lgt_set })
		if node.hasSnd:		charts.append({ "name" : "Sound",		"color" : [0,	0,	0],		"set" : snd_set })
		if node.hasVlt:		charts.append({ "name" : "Voltage",		"color" : [255,	0,	0],		"set" : vlt_set })
		if node.hasAmp:		charts.append({ "name" : "Current",		"color" : [255,	51,	255],	"set" : amp_set })
		
		return charts

	def __str__(self):
		return str(self.js_timestamp) + "-Node" + str(self.node.node_id)

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
