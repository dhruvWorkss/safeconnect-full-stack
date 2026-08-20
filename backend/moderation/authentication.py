from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class WorkspaceTokenSerializer(TokenObtainPairSerializer):
    workspace=serializers.SlugField(write_only=True)
    def validate(self,attrs):
        workspace=attrs.pop("workspace","").lower()
        data=super().validate(attrs)
        if not self.user.organization or self.user.organization.slug!=workspace or not self.user.organization.is_active:
            raise serializers.ValidationError("Invalid company workspace or account.")
        data["user"]={"id":self.user.id,"name":self.user.display_name or self.user.username,"role":self.user.role,"workspace":self.user.organization.slug,"company":self.user.organization.name}
        return data

class WorkspaceTokenView(TokenObtainPairView):
    serializer_class=WorkspaceTokenSerializer
