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


class CAAdmin(admin.ModelAdmin):
	list_display = ('id', '__str__', 'keypath', 'crtpath')


class CSRAdmin(admin.ModelAdmin):
	list_display = ('id', '__str__', 'ca', 'owner', 'created')
	search_fields = ('owner__username','csrfile')
	list_filter = (OwnerFilter,)


class CRTAdmin(admin.ModelAdmin):
	list_display = ('id', '__str__', 'csr', 'owner', 'created')
	search_fields = ('owner__username',)
	list_filter = (OwnerFilter,)


admin.site.register(CAModel, CAAdmin)
admin.site.register(CSRModel, CSRAdmin)
admin.site.register(CRTModel, CRTAdmin)
