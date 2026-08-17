from django.core.management.base import BaseCommand
from datetime import date
from core.models import Event,Venue,Resource,Vendor
class Command(BaseCommand):
    def handle(self,*args,**kwargs):
        v,_=Venue.objects.get_or_create(name='Seminar Hall',defaults={'location':'Main Block','capacity':300,'available':True})
        for name,total in [('Projector',5),('Microphone',10),('Laptop',50)]: Resource.objects.get_or_create(name=name,defaults={'total_quantity':total,'available_quantity':total})
        Vendor.objects.get_or_create(name='ABC Catering',defaults={'service_type':'Catering','phone':'9876543210','email':'catering@example.com','availability':True})
        Vendor.objects.get_or_create(name='XYZ Photography',defaults={'service_type':'Photography','phone':'9876543211','email':'photo@example.com','availability':True})
        Event.objects.get_or_create(name='AI Workshop',defaults={'event_type':'Workshop','date':date.today(),'budget':50000,'expected_participants':100,'venue':v})
        self.stdout.write(self.style.SUCCESS('Demo data created.'))
