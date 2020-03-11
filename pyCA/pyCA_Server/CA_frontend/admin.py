from django.contrib import admin
from django.contrib.auth.models import User
from django.core import urlresolvers

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
	search_fields = ('owner__username',)
	list_filter = (OwnerFilter,)


class CRTAdmin(admin.ModelAdmin):
	list_display = ('id', '__str__', 'csr', 'owner', 'created')
	search_fields = ('owner__username',)
	list_filter = (OwnerFilter,)

	def link_to_user(self, obj):
		link = reverse("admin:auth_user_change", args=[obj.user.id])
		return format_html('<a href="{}">Edit {}</a>', link, obj.user.username)


admin.site.register(CAModel, CAAdmin)
admin.site.register(CSRModel, CSRAdmin)
admin.site.register(CRTModel, CRTAdmin)
