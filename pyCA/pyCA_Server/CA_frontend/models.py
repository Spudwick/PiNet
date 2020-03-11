import uuid
import os

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db import models


def get_uuid_upload_path(inst, filename):
	ext = filename.split('.')[1]
	return "upload/" + str(uuid.uuid4()) + "." + ext

def get_uuid_local_path(inst, filename):
	ext = filename.split('.')[1]
	return "local/" + str(uuid.uuid4()) + "." + ext

def generate_new_crt(csr):
	print("Generating CRT for " + csr.csrfile.name)
	path = settings.MEDIA_ROOT + get_uuid_local_path(None, "dummy.crt")
	print("   path = " + path)
	with open(path, "w") as fp:
		fp.write("")
	return path

def generate_new_ca(name):
	keypath = settings.MEDIA_ROOT + "local/ca/" + name.replace(' ', '_') + ".key"
	crtpath = settings.MEDIA_ROOT + "local/ca/" + name.replace(' ', '_') + ".crt"
	
	print(keypath)
	print(crtpath)

	with open(keypath, "w") as fp:
		fp.write("")
	with open(crtpath, "w") as fp:
		fp.write("")

	return {"key":keypath, "crt":crtpath}


class CAModel(models.Model):
	id = models.AutoField(primary_key=True)
	created = models.DateTimeField(auto_now_add=True)

	name = models.CharField(max_length=100, unique=True)
	# TODO : These crap out if "settings.MEDIA_ROOT/local/ca/" doesn't exist.
	keypath = models.FilePathField(verbose_name="Key File", path=settings.MEDIA_ROOT + "local/ca/", match=".*\.key", blank=True, editable=False)
	crtpath = models.FilePathField(verbose_name="Certificate File", path=settings.MEDIA_ROOT + "local/ca/", match=".*\.crt", blank=True, editable=False)

	class Meta:
		ordering = ['created']
		verbose_name = 'Certificate Authority'
		verbose_name_plural = 'Certificate Authorities'

	def __str__(self):
		return str(self.name)

	def save(self, *args, **kwargs):
		if self.keypath == "" or self.crtpath == "":
			cafiles = generate_new_ca(str(self.name))
			self.keypath = cafiles["key"]
			self.crtpath = cafiles["crt"]

		super().save()


class CSRModel(models.Model):
	id = models.AutoField(primary_key=True)
	created = models.DateTimeField(auto_now_add=True)
	owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)

	ca = models.ForeignKey('CAModel', on_delete=models.CASCADE, verbose_name="Certificate Authority")
	csrfile = models.FileField(	verbose_name="Certificate Signing Request",
								upload_to=get_uuid_upload_path,
								validators=[FileExtensionValidator(allowed_extensions=['csr'])])

	class Meta:
		ordering = ['created']
		verbose_name = 'Signing Request'
		verbose_name_plural = 'Signing Requests'

	def __str__(self):
		return os.path.basename(self.csrfile.name)


class CRTModel(models.Model):
	id = models.AutoField(primary_key=True)
	created = models.DateTimeField(auto_now_add=True)
	owner = models.ForeignKey('auth.User', on_delete=models.CASCADE, editable=False)
	
	csr = models.ForeignKey('CSRModel', on_delete=models.CASCADE, verbose_name="Certificate Signing Request")
	# TODO : This craps out if "settings.MEDIA_ROOT/local/" doesn't exist.
	crtfilepath = models.FilePathField(verbose_name="Certificate File", path=settings.MEDIA_ROOT + "local/", match=".*\.crt", blank=True, editable=False)

	class Meta:
		ordering = ['created']
		verbose_name = 'Certificate'
		verbose_name_plural = 'Certificates'
	
	def __str__(self):
		return os.path.basename(str(self.crtfilepath))

	def save(self, *args, **kwargs):
		self.owner = self.csr.owner
		
		if self.crtfilepath == "":
			self.crtfilepath = generate_new_crt(self.csr)

		super().save()


@receiver(post_delete, sender=CAModel)
def CAModel_post_delete(sender, instance, **kwargs):
	os.remove(instance.keypath)
	os.remove(instance.crtpath)

@receiver(post_delete, sender=CSRModel)
def CSRModel_post_delete(sender, instance, **kwargs):
	instance.csrfile.delete(False)

@receiver(post_delete, sender=CRTModel)
def CRTModel_post_delete(sender, instance, **kwargs):
	os.remove(instance.crtfilepath)
