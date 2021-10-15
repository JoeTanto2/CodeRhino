from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import UserCreationForm, UserChangeForm, CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser, Servers


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = CustomUser
    list_display = ('email', 'authentication_type', 'is_email_verified', 'is_visible', 'is_superuser', 'is_active',)
    list_filter = ('email', 'is_visible', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password', 'authentication_type', 'profile_pic', 'is_email_verified', 'is_visible')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Servers)
