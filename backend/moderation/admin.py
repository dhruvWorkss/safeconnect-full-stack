from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AuditLog, Block, ModerationAction, ModerationCase, Notification, Organization, Report, User
admin.site.register(User,UserAdmin)
admin.site.register([Organization,Report,ModerationCase,ModerationAction,Block,Notification,AuditLog])
