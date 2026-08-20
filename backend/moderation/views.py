from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Avg, Count
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import AuditLog, Block, ModerationAction, ModerationCase, Notification, Report
from .permissions import IsAdmin, IsModerator
from .serializers import AuditSerializer, BlockSerializer, CaseSerializer, NotificationSerializer, RegisterSerializer, ReportSerializer, UserSerializer
User=get_user_model()

def audit(actor,event,target,metadata=None):
    AuditLog.objects.create(actor=actor,event=event,target_type=target.__class__.__name__,target_id=str(target.pk),metadata=metadata or {})

@api_view(["GET"])
@permission_classes([AllowAny])
def health(request): return Response({"status":"healthy","service":"safeconnect-api","time":timezone.now()})

class RegisterView(CreateAPIView):
    permission_classes=[AllowAny]; serializer_class=RegisterSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=User.objects.all().order_by("username"); serializer_class=UserSerializer; search_fields=["username","display_name","email"]
    def get_permissions(self): return [IsAdmin()] if self.action=="list" else [IsAuthenticated()]
    def get_queryset(self):
        return super().get_queryset() if self.request.user.role in ("moderator","admin") else User.objects.filter(pk=self.request.user.pk)

class ReportViewSet(viewsets.ModelViewSet):
    serializer_class=ReportSerializer; filterset_fields=["status","category"]; search_fields=["public_id","description","reported_user__username"]; ordering_fields=["risk_score","created_at","updated_at"]
    def get_queryset(self):
        qs=Report.objects.select_related("reporter","reported_user")
        return qs if self.request.user.role in ("moderator","admin") else qs.filter(reporter=self.request.user)
    def perform_create(self,serializer):
        report=serializer.save(reporter=self.request.user)
        risk={"threat":92,"hate":78,"harassment":68,"impersonation":56,"spam":28,"other":40}[report.category]
        report.risk_score=risk; report.save(update_fields=["risk_score"])
        priority="critical" if risk>=85 else "high" if risk>=65 else "medium" if risk>=40 else "low"
        case=ModerationCase.objects.create(report=report,priority=priority)
        audit(self.request.user,"report.created",report,{"case_id":case.id})
    def get_permissions(self):
        if self.action in ("update","partial_update","destroy"): return [IsModerator()]
        return [IsAuthenticated()]

class BlockViewSet(viewsets.ModelViewSet):
    serializer_class=BlockSerializer
    def get_queryset(self): return Block.objects.filter(blocker=self.request.user).select_related("blocked")
    def perform_create(self,serializer):
        block=serializer.save(blocker=self.request.user); audit(self.request.user,"user.blocked",block)

class CaseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class=CaseSerializer; permission_classes=[IsModerator]; filterset_fields=["status","priority","assigned_to"]; search_fields=["report__public_id","report__reported_user__username","report__description"]; ordering_fields=["report__risk_score","created_at","updated_at"]
    queryset=ModerationCase.objects.select_related("report","report__reporter","report__reported_user","assigned_to").prefetch_related("actions__actor")
    @action(detail=True,methods=["post"])
    def claim(self,request,pk=None):
        case=self.get_object(); case.assigned_to=request.user; case.status=Report.Status.REVIEWING; case.report.status=Report.Status.REVIEWING; case.save(); case.report.save(update_fields=["status"]); ModerationAction.objects.create(case=case,actor=request.user,action="claim"); audit(request.user,"case.claimed",case); return Response(self.get_serializer(case).data)
    @action(detail=True,methods=["post"])
    def act(self,request,pk=None):
        case=self.get_object(); action_name=request.data.get("action"); notes=request.data.get("notes","")
        allowed=dict(ModerationAction._meta.get_field("action").choices)
        if action_name not in allowed: return Response({"action":"Invalid moderation action."},status=400)
        with transaction.atomic():
            ModerationAction.objects.create(case=case,actor=request.user,action=action_name,notes=notes)
            if action_name in ("resolve","dismiss"):
                case.status=Report.Status.RESOLVED if action_name=="resolve" else Report.Status.DISMISSED; case.report.status=case.status; case.resolution_notes=notes; case.report.save(update_fields=["status"])
            elif action_name=="escalate": case.priority="critical"
            case.assigned_to=request.user; case.save(); Notification.objects.create(user=case.report.reporter,message=f"Report {case.report.public_id} was {action_name}d."); audit(request.user,f"case.{action_name}",case,{"notes":notes})
        return Response(self.get_serializer(case).data)

class NotificationViewSet(mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    serializer_class=NotificationSerializer
    def get_queryset(self): return Notification.objects.filter(user=self.request.user)
    @action(detail=True,methods=["post"])
    def read(self,request,pk=None):
        item=self.get_object(); item.read=True; item.save(update_fields=["read"]); return Response(self.get_serializer(item).data)

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=AuditLog.objects.select_related("actor"); serializer_class=AuditSerializer; permission_classes=[IsModerator]; filterset_fields=["event","target_type"]; search_fields=["event","target_id"]

@api_view(["GET"])
@permission_classes([IsModerator])
def dashboard_stats(request):
    open_cases=ModerationCase.objects.exclude(status__in=[Report.Status.RESOLVED,Report.Status.DISMISSED])
    return Response({"open_cases":open_cases.count(),"critical_priority":open_cases.filter(priority="critical").count(),"resolution_rate":round(100*ModerationCase.objects.filter(status=Report.Status.RESOLVED).count()/max(ModerationCase.objects.count(),1),1),"average_risk":round(Report.objects.aggregate(v=Avg("risk_score"))["v"] or 0,1),"unread_notifications":Notification.objects.filter(user=request.user,read=False).count()})
