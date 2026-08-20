from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import AuditLog, Block, ModerationAction, ModerationCase, Notification, Report
User=get_user_model()
class UserSerializer(serializers.ModelSerializer):
    class Meta: model=User; fields=["id","username","email","display_name","role"]
class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True,min_length=8)
    class Meta: model=User; fields=["id","username","email","display_name","password"]
    def create(self,data): return User.objects.create_user(**data)
class ReportSerializer(serializers.ModelSerializer):
    reporter=UserSerializer(read_only=True); reported_user_detail=UserSerializer(source="reported_user",read_only=True)
    class Meta: model=Report; fields=["id","public_id","reporter","reported_user","reported_user_detail","category","description","evidence_url","status","risk_score","created_at","updated_at"]; read_only_fields=["public_id","status","risk_score"]
    def validate_reported_user(self,value):
        if value==self.context["request"].user: raise serializers.ValidationError("You cannot report yourself.")
        return value
    def validate(self,attrs):
        request=self.context["request"]
        if Report.objects.filter(reporter=request.user,reported_user=attrs.get("reported_user"),category=attrs.get("category"),status__in=["open","reviewing"]).exists():
            raise serializers.ValidationError("An active report already exists for this user and category.")
        return attrs
class BlockSerializer(serializers.ModelSerializer):
    class Meta: model=Block; fields=["id","blocker","blocked","created_at"]; read_only_fields=["blocker"]
    def validate_blocked(self,value):
        if value==self.context["request"].user: raise serializers.ValidationError("You cannot block yourself.")
        return value
class ActionSerializer(serializers.ModelSerializer):
    actor=UserSerializer(read_only=True)
    class Meta: model=ModerationAction; fields=["id","actor","action","notes","created_at"]
class CaseSerializer(serializers.ModelSerializer):
    report=ReportSerializer(read_only=True); actions=ActionSerializer(many=True,read_only=True); assigned_to=UserSerializer(read_only=True)
    class Meta: model=ModerationCase; fields=["id","report","assigned_to","status","priority","resolution_notes","actions","created_at","updated_at"]
class NotificationSerializer(serializers.ModelSerializer):
    class Meta: model=Notification; fields="__all__"; read_only_fields=["user"]
class AuditSerializer(serializers.ModelSerializer):
    actor=UserSerializer(read_only=True)
    class Meta: model=AuditLog; fields="__all__"
