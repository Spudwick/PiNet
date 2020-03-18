import uuid
import os

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db import models


def get_uuid_upload_path(inst, filename, extra=""):
	ext = filename.split('.')[1]
	return "upload/" + extra + str(uuid.uuid4()) + "." + ext

def get_uuid_upload_path_ca(inst, filename):
	return get_uuid_upload_path(inst, filename, extra="ca/")

def get_uuid_local_path(inst, filename, extra=""):
	ext = filename.split('.')[1]
	return "local/" + extra + str(uuid.uuid4()) + "." + ext

def generate_new_crt(csr):
	print("Generating CRT for " + csr.csrfile.name)
	path = settings.MEDIA_ROOT + get_uuid_local_path(None, "dummy.crt")
	print("   path = " + path)
	with open(path, "w") as fp:
		fp.write("")
	return path

def generate_new_ca_key():
	path = settings.MEDIA_ROOT + get_uuid_local_path(None, "dummy.key", extra="ca/")
	print("NEW CA KEY AT " + path)
	with open(path, "w") as fp:
		fp.write("")
	return path

def generate_new_ca_crt(key):
	path = settings.MEDIA_ROOT + get_uuid_local_path(None, "dummy.crt", extra="ca/")
	print("NEW CA CRT AT " + path)
	with open(path, "w") as fp:
		fp.write("")
	return path


class CAModel(models.Model):
	id = models.AutoField(primary_key=True)
	created = models.DateTimeField(auto_now_add=True)

	name = models.CharField(max_length=100, unique=True)
	keypath = models.FilePathField(	verbose_name="CA Key File",
									path=settings.MEDIA_ROOT + "local/",
									match=".*\.crt",
									blank=True,
									editable=False)
	crtpath = models.FilePathField(	verbose_name="CA Certificate File",
									path=settings.MEDIA_ROOT + "local/",
									match=".*\.crt",
									blank=True,
									editable=False)

	class Meta:
		ordering = ['created']
		verbose_name = 'Certificate Authority'
		verbose_name_plural = 'Certificate Authorities'

	def __str__(self):
		return str(self.name)

	def save(self, *args, **kwargs):
		print(self.keypath)
		print(self.crtpath)

		if self.keypath == "":
			self.keypath = generate_new_ca_key()
			self.crtpath = generate_new_ca_crt(self.keypath)
		elif self.crtpath == "":
			self.crtpath = generate_new_ca_crt(self.keypath)

		print(self.keypath)

		super().save()


class CSRModel(models.Model):
	id = models.AutoField(primary_key=True)
	created = models.DateTimeField(auto_now_add=True)
	owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)

	ca = models.ForeignKey(	'CAModel',
							on_delete=models.CASCADE,
							verbose_name="Certificate Authority")
	csrfile = models.FileField(	verbose_name="Certificate Signing Request",
								upload_to=get_uuid_upload_path,
								validators=[FileExtensionValidator(allowed_extensions=['csr'])])

	class Meta:
		ordering = ['created']
		verbose_name = 'Signing Request'
		verbose_name_plural = 'Signing Requests'

	def __str__(self):
		return self.csrfile.name


class CRTModel(models.Model):
	id = models.AutoField(primary_key=True)
	created = models.DateTimeField(auto_now_add=True)
	owner = models.ForeignKey('auth.User', on_delete=models.CASCADE, editable=False)
	
	ca = models.ForeignKey(	'CAModel',
							on_delete=models.CASCADE,
							verbose_name="Certificate Authority",
							blank=True,
							editable=False)
	csr = models.ForeignKey(	'CSRModel',
								on_delete=models.CASCADE,
								verbose_name="Certificate Signing Request")
	# TODO : This craps out if "settings.MEDIA_ROOT/local/" doesn't exist.
	crtfilepath = models.FilePathField(	verbose_name="Certificate File",
										path=settings.MEDIA_ROOT + "local/",
										match=".*\.crt",
										blank=True,
										editable=False)

	class Meta:
		ordering = ['created']
		verbose_name = 'Certificate'
		verbose_name_plural = 'Certificates'
	
	def __str__(self):
		return str(self.crtfilepath)

	def save(self, *args, **kwargs):
		self.owner = self.csr.owner
		self.ca = self.csr.ca

		if self.crtfilepath == "":
			self.crtfilepath = generate_new_crt(self.csr)

		super().save()


@receiver(post_delete, sender=CAModel)
def CAModel_post_delete(sender, instance, **kwargs):
	if not instance.keypath == "":
		os.remove(instance.keypath)
	if not instance.crtpath == "":
		os.remove(instance.crtpath)

@receiver(post_delete, sender=CSRModel)
def CSRModel_post_delete(sender, instance, **kwargs):
	instance.csrfile.delete(False)

@receiver(post_delete, sender=CRTModel)
def CRTModel_post_delete(sender, instance, **kwargs):
	os.remove(instance.crtfilepath)
