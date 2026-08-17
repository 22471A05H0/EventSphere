from django.contrib import admin
from .models import Event,Venue,Resource,ResourceAllocation,Attendee,Ticket,Vendor,VendorAssignment,Notification
admin.site.register([Event,Venue,Resource,ResourceAllocation,Attendee,Ticket,Vendor,VendorAssignment,Notification])
