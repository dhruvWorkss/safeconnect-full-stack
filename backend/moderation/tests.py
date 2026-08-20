import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import AuditLog, ModerationCase, Report
User=get_user_model()

@pytest.fixture
def users(db):
    return {"user":User.objects.create_user("reporter",password="strongpass1"),"target":User.objects.create_user("target",password="strongpass1"),"mod":User.objects.create_user("moderator",password="strongpass1",role="moderator")}
@pytest.fixture
def client(): return APIClient()
def auth(client,user): client.force_authenticate(user); return client

@pytest.mark.django_db
def test_report_creates_ranked_case_and_audit(client,users):
    response=auth(client,users["user"]).post("/api/reports/",{"reported_user":users["target"].id,"category":"threat","description":"Credible threat"},format="json")
    assert response.status_code==201; report=Report.objects.get(); assert report.risk_score==92; assert report.case.priority=="critical"; assert AuditLog.objects.filter(event="report.created").exists()
@pytest.mark.django_db
def test_duplicate_active_report_rejected(client,users):
    payload={"reported_user":users["target"].id,"category":"spam","description":"Repeated spam"}; api=auth(client,users["user"]); assert api.post("/api/reports/",payload).status_code==201; assert api.post("/api/reports/",payload).status_code==400
@pytest.mark.django_db
def test_user_cannot_access_moderation_queue(client,users): assert auth(client,users["user"]).get("/api/cases/").status_code==403
@pytest.mark.django_db
def test_moderator_resolves_case(client,users):
    report=Report.objects.create(reporter=users["user"],reported_user=users["target"],category="harassment",description="abuse",risk_score=70); case=ModerationCase.objects.create(report=report,priority="high")
    response=auth(client,users["mod"]).post(f"/api/cases/{case.id}/act/",{"action":"resolve","notes":"Policy violation confirmed"},format="json")
    case.refresh_from_db(); assert response.status_code==200; assert case.status=="resolved"; assert case.actions.count()==1
@pytest.mark.django_db
def test_cannot_report_self(client,users):
    response=auth(client,users["user"]).post("/api/reports/",{"reported_user":users["user"].id,"category":"other","description":"x"},format="json"); assert response.status_code==400
