
from django.db import models

from pytz import timezone

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

	@property
	def sensors(self):
		sensors = []
		if self.hasTmp:
			sensors.append("temperature")
		if self.hasHum:
			sensors.append("humidity")
		if self.hasLgt:
			sensors.append("light")
		if self.hasSnd:
			sensors.append("sound")
		if self.hasVlt:
			sensors.append("voltage")
		if self.hasAmp:
			sensors.append("current")
		
		return sensors

	def __str__(self):
		return "Node" + str(self.node_id)

	def save(self, *args, **kwargs):
		self.location = self.location.title()

		super().save(*args, **kwargs)

	def jsNodeChart(self, depth=None, period=None):
		return NodeReading.jsNodeChart(node=self, depth=depth, period=period)


class NodeReading(models.Model):
	class Meta:
		verbose_name_plural = "Node Readings"
		db_table = "node_readings"

	timestamp = models.DateTimeField(auto_now_add=True)
	node = models.ForeignKey(Node, on_delete=models.CASCADE)

	temperature = models.FloatField(default=0)
	humidity = models.FloatField(default=0)
	light = models.FloatField(default=0)
	sound = models.FloatField(default=0)
	voltage = models.FloatField(default=0)
	current = models.FloatField(default=0)

	@property
	def js_timestamp(self):
		if not self.timestamp.tzinfo == timezone('UTC'):
			raise ValueError("Timezone Mismatch : Timestamp Timezone not UTC (%s)!" % str(self.timestamp.tzinfo))

		return self.timestamp.strftime("%Y-%m-%dT%H:%M:%S") + ".000Z"		# 'Z' denotes this is UTC format

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
	def searchSensor(cls, sensor, depth=None, period=None):
		charts = []
		for node in Node.objects.all():
			if sensor in node.sensors:
				dataset = []
				for entry in NodeReading.searchNode(node, depth, period):
					dataset.append({ "timestamp" : entry.timestamp, "value" : entry[sensor] })

				if not dataset == []:
					charts.append({ node : dataset })

		return charts

	@classmethod
	def jsNodeChart(cls, node, depth=None, period=None):
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

	@classmethod
	def jsSensorChart(cls, sensor, depth=None, period=None):
		db = cls.searchSensor(sensor, depth, period)

		charts = []
		for entry in db:
			for node,dataset in entry.items():
				node_set = []
				for entry in dataset:
					node_set.append({ "t" : entry["timestamp"], "y" : entry["value"] })
				charts.append({ "name" : node.location.title(), "color" : [255, 0, 0], "set" : node_set })

		return charts

	def __getitem__(self, key):
		return getattr(self, key.lower())

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
