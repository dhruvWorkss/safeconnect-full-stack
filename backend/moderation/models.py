import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class Organization(models.Model):
    name=models.CharField(max_length=120)
    slug=models.SlugField(max_length=80,unique=True,db_index=True)
    allowed_email_domain=models.CharField(max_length=120,blank=True)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class User(AbstractUser):
    class Role(models.TextChoices): USER="user","User"; MODERATOR="moderator","Moderator"; ADMIN="admin","Admin"
    role=models.CharField(max_length=16,choices=Role.choices,default=Role.USER,db_index=True)
    display_name=models.CharField(max_length=120,blank=True)
    organization=models.ForeignKey(Organization,on_delete=models.PROTECT,null=True,blank=True,related_name="members")

class Report(models.Model):
    class Category(models.TextChoices): HARASSMENT="harassment","Harassment"; THREAT="threat","Threat"; HATE="hate","Hate speech"; SPAM="spam","Spam"; IMPERSONATION="impersonation","Impersonation"; OTHER="other","Other"
    class Status(models.TextChoices): OPEN="open","Open"; REVIEWING="reviewing","Reviewing"; RESOLVED="resolved","Resolved"; DISMISSED="dismissed","Dismissed"
    public_id=models.CharField(max_length=16,unique=True,editable=False,db_index=True)
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE,null=True,related_name="reports")
    reporter=models.ForeignKey(User,on_delete=models.CASCADE,related_name="reports_made")
    reported_user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="reports_received")
    category=models.CharField(max_length=24,choices=Category.choices,db_index=True)
    description=models.TextField(); evidence_url=models.URLField(blank=True)
    status=models.CharField(max_length=16,choices=Status.choices,default=Status.OPEN,db_index=True)
    risk_score=models.PositiveSmallIntegerField(default=0,db_index=True)
    created_at=models.DateTimeField(auto_now_add=True,db_index=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        ordering=["-risk_score","-created_at"]
        constraints=[models.UniqueConstraint(fields=["reporter","reported_user","category"],condition=models.Q(status__in=["open","reviewing"]),name="unique_active_report")]
        indexes=[models.Index(fields=["status","-risk_score","-created_at"])]
    def save(self,*args,**kwargs):
        if not self.public_id: self.public_id=f"SC-{str(uuid.uuid4().int)[-6:]}"
        super().save(*args,**kwargs)

class ModerationCase(models.Model):
    report=models.OneToOneField(Report,on_delete=models.CASCADE,related_name="case")
    assigned_to=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name="assigned_cases")
    status=models.CharField(max_length=16,choices=Report.Status.choices,default=Report.Status.OPEN,db_index=True)
    priority=models.CharField(max_length=12,choices=[("low","Low"),("medium","Medium"),("high","High"),("critical","Critical")],default="medium",db_index=True)
    resolution_notes=models.TextField(blank=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=["-report__risk_score","-created_at"]

class ModerationAction(models.Model):
    case=models.ForeignKey(ModerationCase,on_delete=models.CASCADE,related_name="actions")
    actor=models.ForeignKey(User,on_delete=models.PROTECT)
    action=models.CharField(max_length=24,choices=[("claim","Claim"),("warn","Warn"),("suspend","Suspend"),("ban","Ban"),("escalate","Escalate"),("resolve","Resolve"),("dismiss","Dismiss")])
    notes=models.TextField(blank=True); created_at=models.DateTimeField(auto_now_add=True)

class Block(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE,null=True,related_name="blocks")
    blocker=models.ForeignKey(User,on_delete=models.CASCADE,related_name="blocks_created")
    blocked=models.ForeignKey(User,on_delete=models.CASCADE,related_name="blocked_by")
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=["blocker","blocked"],name="unique_block")]

class Notification(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE,null=True,related_name="notifications")
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="notifications")
    message=models.CharField(max_length=255); read=models.BooleanField(default=False,db_index=True); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=["-created_at"]

class AuditLog(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE,null=True,related_name="audit_logs")
    actor=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    event=models.CharField(max_length=80,db_index=True); target_type=models.CharField(max_length=40); target_id=models.CharField(max_length=64); metadata=models.JSONField(default=dict,blank=True); created_at=models.DateTimeField(auto_now_add=True,db_index=True)
    class Meta: ordering=["-created_at"]
