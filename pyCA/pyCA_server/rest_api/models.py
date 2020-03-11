from django.db import models


class Message(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	owner = models.ForeignKey('auth.User', related_name='messages', on_delete=models.CASCADE)

	message = models.CharField(max_length=100, blank=True, default='')

	class Meta:
		ordering = ['created']
