from django.shortcuts import render
from django.http import HttpResponse

from .models import Node, NodeReading


def index(request):
	nodes = Node.objects.all()[:5]

	array = []
	for node in nodes:
		datasets = []
		
		data = node.getTmps()
		if not data == None and not len(data) == 0:
			datasets.append({ "name" : "Temperature", "color" : [255,0,0,0.5], "set" : data })

		data = node.getHums()
		if not data == None and not len(data) == 0:
			datasets.append({ "name" : "Humidity", "color" : [0,0,255,0.5], "set" : data })

		data = node.getLgts()
		if not data == None and not len(data) == 0:
			datasets.append({ "name" : "Light", "color" : [255,255,51,0.5], "set" : data })

		data = node.getSnds()
		if not data == None and not len(data) == 0:
			datasets.append({ "name" : "Sound", "color" : [0,0,255,0.5], "set" : data })

		data = node.getVlts()
		if not data == None and not len(data) == 0:
			datasets.append({ "name" : "Voltage", "color" : [0,0,255,0.5], "set" : data })

		data = node.getAmps()
		if not data == None and not len(data) == 0:
			datasets.append({ "name" : "Current", "color" : [0,0,255,0.5], "set" : data })

		array.append({ "id" : node.node_id, "location" : node.location, "datasets" : datasets })

	return render(request, 'sensors/index.html', {'nodes': array})
