from django.db import models


class Message(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	message = models.CharField(max_length=100, blank=True, default='')

	class Meta:
		ordering = ['created']