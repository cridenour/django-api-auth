from django.contrib import admin
from api.models import APIToken


class TokenAdmin(admin.ModelAdmin):
    """
    Allow tokens to be refreshed from the admin
    """
    actions = ['refresh']
    list_display = ('user', 'active', 'expires')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')

    def refresh(self, request, queryset):
        for token in queryset:
            token.refresh()

        if len(queryset) == 1:
            message_bit = "1 token was"
        else:
            message_bit = "%s tokens were" % len(queryset)
        self.message_user(request, "%s refreshed." % message_bit)
    refresh.short_description = 'Refresh API Token(s)'

admin.site.register(APIToken, TokenAdmin)