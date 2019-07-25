from django.shortcuts import render
from django.http import HttpResponse

def index(request):
	array = range(0,10)
	return render(request, 'sensors/index.html', { 'test': "hello", 'charts': array })
