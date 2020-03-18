from django.contrib import admin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html

from .models import CAModel, CSRModel, CRTModel


class OwnerFilter(admin.SimpleListFilter):
	title = "Owner"
	parameter_name = "owner"

	def lookups(self, request, model_admin):
		users = [(str(u), str(u)) for u in User.objects.all()]
		return users

	def queryset(self, request, queryset):
		if self.value() == None:
			return queryset
		else:
			return queryset.filter(owner__username=self.value())


class CAFilter(admin.SimpleListFilter):
	title = "Certificate Authority"
	parameter_name = "ca"

	def lookups(self, request, model_admin):
		users = [(str(ca), str(ca)) for ca in CAModel.objects.all()]
		return users

	def queryset(self, request, queryset):
		if self.value() == None:
			return queryset
		else:
			return queryset.filter(ca__name=self.value())


class CAAdmin(admin.ModelAdmin):
	list_display = ('id', '__str__', 'keyfile', 'crtfile')


class CSRAdmin(admin.ModelAdmin):
	list_display = ('id', '__str__', 'ca', 'owner', 'created')
	search_fields = ('owner__username', 'csrfile')
	list_filter = (OwnerFilter, CAFilter)


class CRTAdmin(admin.ModelAdmin):
	list_display = ('id', '__str__', 'csr', 'ca', 'owner', 'created')
	search_fields = ('owner__username',)
	list_filter = (OwnerFilter, CAFilter)


admin.site.register(CAModel, CAAdmin)
admin.site.register(CSRModel, CSRAdmin)
admin.site.register(CRTModel, CRTAdmin)
