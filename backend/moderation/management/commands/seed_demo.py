from django.core.management.base import BaseCommand
from moderation.models import ModerationCase, Organization, Report, User

class Command(BaseCommand):
    help="Create portfolio demo accounts and moderation cases"
    def handle(self,*args,**kwargs):
        organization,_=Organization.objects.get_or_create(slug="nova-social",defaults={"name":"Nova Social","allowed_email_domain":"novasocial.com"})
        moderator,_=User.objects.get_or_create(username="moderator",defaults={"display_name":"Jordan Davis","role":"moderator","email":"moderator@novasocial.com","organization":organization}); moderator.organization=organization; moderator.set_password("SafeConnect123!"); moderator.save()
        reporter,_=User.objects.get_or_create(username="reporter",defaults={"display_name":"Alex Morgan","organization":organization}); reporter.organization=organization; reporter.set_password("SafeConnect123!"); reporter.save()
        samples=[("maya.chen","Maya Chen","threat",92,"critical","Targeted threatening language in a community thread."),("noah.williams","Noah Williams","harassment",78,"high","Repeated targeted harassment across direct messages."),("priya.nair","Priya Nair","hate",71,"high","Hateful content directed at a protected group.")]
        for username,name,category,risk,priority,description in samples:
            target,_=User.objects.get_or_create(username=username,defaults={"display_name":name,"organization":organization}); target.organization=organization; target.save(update_fields=["organization"])
            report,_=Report.objects.get_or_create(reporter=reporter,reported_user=target,category=category,defaults={"organization":organization,"description":description,"risk_score":risk}); report.organization=organization; report.save(update_fields=["organization"])
            ModerationCase.objects.get_or_create(report=report,defaults={"priority":priority})
        self.stdout.write(self.style.SUCCESS("Demo ready: nova-social / moderator / SafeConnect123!"))
