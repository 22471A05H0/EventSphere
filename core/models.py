from django.db import models

class Event(models.Model):
    STATUS=[('Created','Created'),('Execution','Execution'),('Completed','Completed')]
    name=models.CharField(max_length=200)
    event_type=models.CharField(max_length=100)
    date=models.DateField()
    budget=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    expected_participants=models.PositiveIntegerField(default=0)
    status=models.CharField(max_length=20,choices=STATUS,default='Created')
    venue=models.ForeignKey('Venue',null=True,blank=True,on_delete=models.SET_NULL,related_name='events')
    def __str__(self): return self.name

class Venue(models.Model):
    name=models.CharField(max_length=150)
    location=models.CharField(max_length=200)
    capacity=models.PositiveIntegerField()
    available=models.BooleanField(default=True)
    def __str__(self): return self.name

class Resource(models.Model):
    name=models.CharField(max_length=150)
    total_quantity=models.PositiveIntegerField(default=0)
    available_quantity=models.PositiveIntegerField(default=0)
    def __str__(self): return self.name

class ResourceAllocation(models.Model):
    event=models.ForeignKey(Event,on_delete=models.CASCADE,related_name='resource_allocations')
    resource=models.ForeignKey(Resource,on_delete=models.CASCADE,related_name='allocations')
    quantity=models.PositiveIntegerField()
    status=models.CharField(max_length=20,default='Allocated')

class Attendee(models.Model):
    STATUS=[('Registered','Registered'),('Checked In','Checked In'),('Absent','Absent'),('Cancelled','Cancelled')]
    registration_id=models.CharField(max_length=30,unique=True)
    name=models.CharField(max_length=120)
    email=models.EmailField()
    phone=models.CharField(max_length=10)
    college=models.CharField(max_length=150)
    department=models.CharField(max_length=100,blank=True)
    event=models.ForeignKey(Event,on_delete=models.CASCADE,related_name='attendees')
    attendance_status=models.CharField(max_length=20,choices=STATUS,default='Registered')

class Ticket(models.Model):
    ticket_id=models.CharField(max_length=30,unique=True)
    event=models.ForeignKey(Event,on_delete=models.CASCADE)
    attendee=models.OneToOneField(Attendee,on_delete=models.CASCADE,related_name='ticket')
    qr_code=models.ImageField(upload_to='qr_codes/',blank=True,null=True)
    issue_date=models.DateField(auto_now_add=True)

class Vendor(models.Model):
    name=models.CharField(max_length=150)
    service_type=models.CharField(max_length=100)
    phone=models.CharField(max_length=10)
    email=models.EmailField()
    availability=models.BooleanField(default=True)
    quality=models.PositiveSmallIntegerField(default=0)
    timeliness=models.PositiveSmallIntegerField(default=0)
    cost_rating=models.PositiveSmallIntegerField(default=0)
    communication=models.PositiveSmallIntegerField(default=0)
    overall_rating=models.DecimalField(max_digits=3,decimal_places=1,default=0)
    def __str__(self): return self.name

class VendorAssignment(models.Model):
    STATUS=[('Assigned','Assigned'),('Completed','Completed'),('Cancelled','Cancelled')]
    event=models.ForeignKey(Event,on_delete=models.CASCADE,related_name='vendor_assignments')
    vendor=models.ForeignKey(Vendor,on_delete=models.CASCADE,related_name='assignments')
    service=models.CharField(max_length=100)
    status=models.CharField(max_length=20,choices=STATUS,default='Assigned')

class Notification(models.Model):
    recipient_type=models.CharField(max_length=20,choices=[('Participant','Participant'),('Vendor','Vendor')])
    recipient=models.CharField(max_length=150)
    message=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    sent=models.BooleanField(default=False)
