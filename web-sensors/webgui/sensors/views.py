from django.shortcuts import render
from django.http import HttpResponse

from .models import Node, NodeReading


def index(request):
	nodes = Node.objects.all()[:5]

	data = []
	for node in nodes:
		data.append({ "node" : node, "readings" : NodeReading.objects.filter(node=node) })

	return render(request, 'sensors/index.html', {'data': data})
