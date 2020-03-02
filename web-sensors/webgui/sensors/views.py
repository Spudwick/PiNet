from django.shortcuts import render
from django.http import HttpResponse

from .models import Node, NodeReading


def index(request):

	nodes = [ {
		"id" : node.node_id,
		"location" : node.location,
		"charts" : node.jsNodeChart()
	} for node in Node.objects.all() ]

	print(NodeReading.jsSensorChart("temperature"))

	return render(request, 'sensors/index.html', {'nodes': nodes })
