from django.core.management.base import BaseCommand
from moderation.models import ModerationCase, Report, User

class Command(BaseCommand):
    help="Create portfolio demo accounts and moderation cases"
    def handle(self,*args,**kwargs):
        moderator,_=User.objects.get_or_create(username="moderator",defaults={"display_name":"Jordan Davis","role":"moderator","email":"moderator@safeconnect.dev"}); moderator.set_password("SafeConnect123!"); moderator.save()
        reporter,_=User.objects.get_or_create(username="reporter",defaults={"display_name":"Alex Morgan"}); reporter.set_password("SafeConnect123!"); reporter.save()
        samples=[("maya.chen","Maya Chen","threat",92,"critical","Targeted threatening language in a community thread."),("noah.williams","Noah Williams","harassment",78,"high","Repeated targeted harassment across direct messages."),("priya.nair","Priya Nair","hate",71,"high","Hateful content directed at a protected group.")]
        for username,name,category,risk,priority,description in samples:
            target,_=User.objects.get_or_create(username=username,defaults={"display_name":name})
            report,_=Report.objects.get_or_create(reporter=reporter,reported_user=target,category=category,defaults={"description":description,"risk_score":risk})
            ModerationCase.objects.get_or_create(report=report,defaults={"priority":priority})
        self.stdout.write(self.style.SUCCESS("Demo ready: moderator / SafeConnect123!"))
