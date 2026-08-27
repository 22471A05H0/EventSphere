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

class Budget(models.Model):
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        related_name="budget_record"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return f"{self.event.name} - ₹{self.amount}"

    def spent(self):
        return sum(
            expense.amount
            for expense in self.event.expenses.filter(
                status="PAID"
            )
        )

    def remaining(self):
        return self.amount - self.spent()


class Expense(models.Model):

    CATEGORY_CHOICES = [
        ("Venue", "Venue"),
        ("Catering", "Catering"),
        ("Equipment", "Equipment"),
        ("Transportation", "Transportation"),
        ("Decoration", "Decoration"),
        ("Marketing", "Marketing"),
        ("Photography", "Photography"),
        ("Security", "Security"),
        ("Other", "Other"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("PAID", "Paid"),
        ("REJECTED", "Rejected"),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="expenses"
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    description = models.CharField(max_length=200)

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    payment_method = models.CharField(
        max_length=50,
        blank=True
    )

    invoice_number = models.CharField(
        max_length=100,
        blank=True
    )

    expense_date = models.DateField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.category} - ₹{self.amount}"


class Revenue(models.Model):

    SOURCE_CHOICES = [
        ("Registration", "Registration"),
        ("Sponsorship", "Sponsorship"),
        ("Vendor Fee", "Vendor Fee"),
        ("Donation", "Donation"),
        ("Other", "Other"),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="revenues"
    )

    source = models.CharField(
        max_length=50,
        choices=SOURCE_CHOICES
    )

    description = models.CharField(
        max_length=200,
        blank=True
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    received_date = models.DateField(
        auto_now_add=True
    )

    payment_method = models.CharField(
        max_length=50,
        blank=True
    )

    def __str__(self):
        return f"{self.source} - ₹{self.amount}"