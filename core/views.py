from io import BytesIO
import qrcode
from django.contrib import messages
from django.core.files.base import ContentFile
from django.db.models import Count,Sum
from django.shortcuts import get_object_or_404,redirect,render
from .models import (
    Event,
    Venue,
    Resource,
    ResourceAllocation,
    Attendee,
    Ticket,
    Vendor,
    VendorAssignment,
    Notification,
    Budget,
    Expense,
    Revenue,
    Sponsorship,
    Approval,
    Reminder,
    APIActivityLog
)
from .forms import (
    EventForm,
    VenueForm,
    ResourceForm,
    AttendeeForm,
    VendorForm,
    AllocationForm,
    AssignmentForm,
    RatingForm,
    NotificationForm,
    BudgetForm,
    ExpenseForm,
    RevenueForm,
    SponsorshipForm,
    ApprovalForm,
    ReminderForm
)
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


def dashboard(request):
    events=Event.objects.select_related('venue').order_by('-id')
    return render(request,'dashboard.html',{'events':events,'event_count':events.count(),'attendee_count':Attendee.objects.count(),'checked_in':Attendee.objects.filter(attendance_status='Checked In').count(),'vendor_count':Vendor.objects.count(),'resource_count':Resource.objects.count()})

def create_event(request):
    form=EventForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        e=form.save(); messages.success(request,'Event created. Continue with venue and resources.'); return redirect('event_detail',e.id)
    return render(request,'form.html',{'form':form,'title':'Create Event','back':'/'})

def event_detail(request,event_id): return render(request,'event_detail.html',{'event':get_object_or_404(Event.objects.select_related('venue'),id=event_id)})

def venues(request):
    form=VenueForm(request.POST or None)
    if request.method=='POST' and form.is_valid(): form.save(); messages.success(request,'Venue added.'); return redirect('venues')
    return render(request,'venues.html',{'form':form,'venues':Venue.objects.all()})

def select_venue(request,event_id):
    event=get_object_or_404(Event,id=event_id)
    if request.method=='POST':
        venue=get_object_or_404(Venue,id=request.POST.get('venue_id'))
        if not venue.available: messages.error(request,'Venue is unavailable.')
        elif venue.capacity<event.expected_participants: messages.error(request,f'Capacity conflict: {venue.capacity} < {event.expected_participants}.')
        elif Event.objects.filter(venue=venue,date=event.date).exclude(id=event.id).exists(): messages.error(request,'Venue conflict: already booked on this date.')
        else: event.venue=venue; event.save(); messages.success(request,'Venue selected.'); return redirect('event_detail',event.id)
    return render(request,'select_venue.html',{'event':event,'venues':Venue.objects.all()})

def resources(request):
    form=ResourceForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        r=form.save(); r.available_quantity=min(r.available_quantity,r.total_quantity); r.save(); messages.success(request,'Resource added.'); return redirect('resources')
    return render(request,'resources.html',{'form':form,'resources':Resource.objects.all()})

def allocate_resources(request,event_id):
    event=get_object_or_404(Event,id=event_id); form=AllocationForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        r=form.cleaned_data['resource']; q=form.cleaned_data['quantity']
        if q>r.available_quantity: messages.error(request,f'Only {r.available_quantity} unit(s) available.')
        else: ResourceAllocation.objects.create(event=event,resource=r,quantity=q); r.available_quantity-=q; r.save(); messages.success(request,'Resource allocated.'); return redirect('allocate_resources',event.id)
    return render(request,'allocate_resources.html',{'event':event,'form':form,'allocations':event.resource_allocations.select_related('resource')})

def register_attendee(request,event_id):
    event=get_object_or_404(Event,id=event_id); form=AttendeeForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        cd=form.cleaned_data
        if Attendee.objects.filter(event=event,email=cd['email']).exists() or Attendee.objects.filter(event=event,phone=cd['phone']).exists(): form.add_error(None,'Duplicate registration: email or phone is already registered.')
        elif event.attendees.count()>=event.expected_participants: form.add_error(None,'Registration closed: participant capacity reached.')
        else:
            a=form.save(commit=False); a.event=event; a.registration_id=f'REG{Attendee.objects.count()+1001}'; a.save()
            t=Ticket.objects.create(ticket_id=f'TKT{Ticket.objects.count()+1001}',event=event,attendee=a)
            img=qrcode.make(f'{t.ticket_id}|{a.registration_id}|{a.id}'); buf=BytesIO(); img.save(buf,format='PNG'); t.qr_code.save(f'{t.ticket_id}.png',ContentFile(buf.getvalue()),save=True)
            Notification.objects.create(recipient_type='Participant',recipient=a.email,message=f'Registration confirmed for {event.name}',sent=True)
            messages.success(request,'Registration successful. Ticket and QR generated.'); return redirect('ticket_detail',a.id)
    return render(request,'register.html',{'form':form,'event':event})

def ticket_detail(request,attendee_id):
    a=get_object_or_404(Attendee.objects.select_related('event'),id=attendee_id); return render(request,'ticket.html',{'attendee':a,'ticket':a.ticket})

def checkin(request):
    attendee=None
    if request.method=='POST':
        try:
            t=Ticket.objects.select_related('attendee','event').get(ticket_id=request.POST.get('ticket_id','').strip()); attendee=t.attendee
            if attendee.attendance_status=='Checked In': messages.info(request,'Already checked in.')
            elif attendee.attendance_status=='Cancelled': messages.error(request,'Cancelled registration cannot check in.')
            else: attendee.attendance_status='Checked In'; attendee.save(); messages.success(request,f'{attendee.name} checked in successfully.')
        except Ticket.DoesNotExist: messages.error(request,'Invalid ticket ID.')
    return render(request,'checkin.html',{'attendee':attendee})

def vendors(request):
    form=VendorForm(request.POST or None)
    if request.method=='POST' and form.is_valid(): form.save(); messages.success(request,'Vendor added.'); return redirect('vendors')
    return render(request,'vendors.html',{'form':form,'vendors':Vendor.objects.all()})

def assign_vendors(request,event_id):
    event=get_object_or_404(Event,id=event_id); form=AssignmentForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        a=form.save(commit=False); a.event=event; a.save(); Notification.objects.create(recipient_type='Vendor',recipient=a.vendor.email,message=f'Assigned to {event.name} for {a.service}.',sent=True); messages.success(request,'Vendor assigned.'); return redirect('assign_vendors',event.id)
    return render(request,'assign_vendors.html',{'event':event,'form':form,'assignments':event.vendor_assignments.select_related('vendor')})

def rate_vendor(request,vendor_id):
    v=get_object_or_404(Vendor,id=vendor_id); form=RatingForm(request.POST or None,instance=v)
    if request.method=='POST' and form.is_valid():
        v=form.save(commit=False); v.overall_rating=round(sum([v.quality,v.timeliness,v.cost_rating,v.communication])/4,1); v.save(); messages.success(request,'Vendor performance saved.'); return redirect('vendors')
    return render(request,'form.html',{'form':form,'title':f'Rate Vendor: {v.name}','back':'vendors'})

def notifications(request):
    form=NotificationForm(request.POST or None)
    if request.method=='POST' and form.is_valid(): n=form.save(commit=False); n.sent=True; n.save(); messages.success(request,'Notification recorded.'); return redirect('notifications')
    return render(request,'notifications.html',{'form':form,'notifications':Notification.objects.order_by('-id')})

def reports(request):
    events=Event.objects.select_related('venue').annotate(participants=Count('attendees'),allocated_units=Sum('resource_allocations__quantity'))
    return render(request,'reports.html',{'events':events,'total_events':Event.objects.count(),'total_attendees':Attendee.objects.count(),'checked_in':Attendee.objects.filter(attendance_status='Checked In').count(),'total_vendors':Vendor.objects.count(),'total_venues':Venue.objects.count()})

def finance_dashboard(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    budget, created = Budget.objects.get_or_create(
        event=event,
        defaults={"amount": 0}
    )

    expenses = Expense.objects.filter(event=event)

    revenues = Revenue.objects.filter(event=event)

    total_expenses = sum(
        expense.amount
        for expense in expenses
        if expense.status == "PAID"
    )

    total_revenue = sum(
        revenue.amount
        for revenue in revenues
    )

    remaining = budget.amount - total_expenses

    profit = total_revenue - total_expenses

    return render(
        request,
        "finance/dashboard.html",
        {
            "event": event,
            "budget": budget,
            "expenses": expenses,
            "revenues": revenues,
            "total_expenses": total_expenses,
            "total_revenue": total_revenue,
            "remaining": remaining,
            "profit": profit,
        }
    )


def set_budget(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    budget, created = Budget.objects.get_or_create(
        event=event
    )

    if request.method == "POST":

        form = BudgetForm(
            request.POST,
            instance=budget
        )

        if form.is_valid():
            form.save()
            return redirect(
                "finance_dashboard",
                event_id=event.id
            )

    else:

        form = BudgetForm(
            instance=budget
        )

    return render(
        request,
        "finance/budget.html",
        {
            "event": event,
            "form": form,
        }
    )


def add_expense(request, event_id):

    event = get_object_or_404(
        Event,
        id=event_id
    )

    if request.method == "POST":

        form = ExpenseForm(request.POST)

        if form.is_valid():

            expense = form.save(
                commit=False
            )

            expense.event = event
            expense.save()

            return redirect(
                "finance_dashboard",
                event_id=event.id
            )

    else:

        form = ExpenseForm()

    return render(
        request,
        "finance/expense_form.html",
        {
            "event": event,
            "form": form,
        }
    )


def add_revenue(request, event_id):

    event = get_object_or_404(
        Event,
        id=event_id
    )

    if request.method == "POST":

        form = RevenueForm(request.POST)

        if form.is_valid():

            revenue = form.save(
                commit=False
            )

            revenue.event = event
            revenue.save()

            return redirect(
                "finance_dashboard",
                event_id=event.id
            )

    else:

        form = RevenueForm()

    return render(
        request,
        "finance/revenue_form.html",
        {
            "event": event,
            "form": form,
        }
    )

def sponsorships(request, event_id):

    event = get_object_or_404(
        Event,
        id=event_id
    )

    form = SponsorshipForm(
        request.POST or None
    )

    if request.method == "POST" and form.is_valid():

        sponsorship = form.save(
            commit=False
        )

        sponsorship.event = event
        sponsorship.save()

        messages.success(
            request,
            "Sponsorship added successfully."
        )

        return redirect(
            "sponsorships",
            event_id=event.id
        )

    sponsors = Sponsorship.objects.filter(
        event=event
    ).order_by("-created_at")

    total_sponsorship = sum(
        sponsor.amount
        for sponsor in sponsors
        if sponsor.status in ["APPROVED", "RECEIVED"]
    )

    return render(
        request,
        "sponsorships.html",
        {
            "event": event,
            "form": form,
            "sponsors": sponsors,
            "total_sponsorship": total_sponsorship,
        }
    )

def approve_sponsorship(request, sponsorship_id):

    sponsorship = get_object_or_404(
        Sponsorship,
        id=sponsorship_id
    )

    if request.method == "POST":

        action = request.POST.get("action")

        if action == "approve":

            sponsorship.status = "APPROVED"
            sponsorship.save()

            Revenue.objects.create(
                event=sponsorship.event,
                source="Sponsorship",
                description=(
                    f"Sponsorship from "
                    f"{sponsorship.sponsor_name}"
                ),
                amount=sponsorship.amount,
                payment_method="Sponsorship"
            )

            messages.success(
                request,
                "Sponsorship approved."
            )

        elif action == "reject":

            sponsorship.status = "REJECTED"
            sponsorship.save()

            messages.warning(
                request,
                "Sponsorship rejected."
            )

        return redirect(
            "sponsorships",
            event_id=sponsorship.event.id
        )

    return render(
        request,
        "approve_sponsorship.html",
        {
            "sponsorship": sponsorship
        }
    )

def request_expense_approval(request, expense_id):

    expense = get_object_or_404(
        Expense,
        id=expense_id
    )

    if expense.status != "PENDING":

        messages.warning(
            request,
            "Only pending expenses can be submitted for approval."
        )

        return redirect(
            "finance_dashboard",
            event_id=expense.event.id
        )

    if request.method == "POST":

        approval = Approval.objects.create(
            approval_type="EXPENSE",
            event=expense.event,
            expense=expense,
            requested_by=(
                request.user.username
                if request.user.is_authenticated
                else "System"
            ),
            comments=request.POST.get(
                "comments",
                ""
            )
        )

        Notification.objects.create(
            recipient_type="Participant",
            recipient="Finance Manager",
            message=(
                f"Expense approval requested for "
                f"{expense.event.name}: "
                f"₹{expense.amount}"
            ),
            sent=True
        )

        messages.success(
            request,
            "Expense approval request submitted."
        )

        return redirect(
            "finance_dashboard",
            event_id=expense.event.id
        )

    return render(
        request,
        "finance/request_approval.html",
        {
            "expense": expense
        }
    )

def approve_sponsorship(request, sponsorship_id):

    sponsorship = get_object_or_404(
        Sponsorship,
        id=sponsorship_id
    )

    if request.method == "POST":

        action = request.POST.get("action")

        if action == "approve":

            sponsorship.status = "APPROVED"
            sponsorship.save()

            Revenue.objects.create(
                event=sponsorship.event,
                source="Sponsorship",
                description=(
                    f"Sponsorship from "
                    f"{sponsorship.sponsor_name}"
                ),
                amount=sponsorship.amount,
                payment_method="Sponsorship"
            )

            messages.success(
                request,
                "Sponsorship approved."
            )

        elif action == "reject":

            sponsorship.status = "REJECTED"
            sponsorship.save()

            messages.warning(
                request,
                "Sponsorship rejected."
            )

        return redirect(
            "sponsorships",
            event_id=sponsorship.event.id
        )

    return render(
        request,
        "approve_sponsorship.html",
        {
            "sponsorship": sponsorship
        }
    )

def request_expense_approval(request, expense_id):

    expense = get_object_or_404(
        Expense,
        id=expense_id
    )

    if expense.status != "PENDING":

        messages.warning(
            request,
            "Only pending expenses can be submitted for approval."
        )

        return redirect(
            "finance_dashboard",
            event_id=expense.event.id
        )

    if request.method == "POST":

        approval = Approval.objects.create(
            approval_type="EXPENSE",
            event=expense.event,
            expense=expense,
            requested_by=(
                request.user.username
                if request.user.is_authenticated
                else "System"
            ),
            comments=request.POST.get(
                "comments",
                ""
            )
        )

        Notification.objects.create(
            recipient_type="Participant",
            recipient="Finance Manager",
            message=(
                f"Expense approval requested for "
                f"{expense.event.name}: "
                f"₹{expense.amount}"
            ),
            sent=True
        )

        messages.success(
            request,
            "Expense approval request submitted."
        )

        return redirect(
            "finance_dashboard",
            event_id=expense.event.id
        )

    return render(
        request,
        "finance/request_approval.html",
        {
            "expense": expense
        }
    )

def approval_dashboard(request):

    approvals = Approval.objects.select_related(
        "event",
        "expense",
        "sponsorship"
    ).order_by("-created_at")

    return render(
        request,
        "approvals.html",
        {
            "approvals": approvals
        }
    )

def process_approval(request, approval_id):

    approval = get_object_or_404(
        Approval,
        id=approval_id
    )

    if request.method == "POST":

        action = request.POST.get(
            "action"
        )

        if action == "approve":

            approval.status = "APPROVED"

            approval.approved_by = (
                request.user.username
                if request.user.is_authenticated
                else "Admin"
            )

            approval.comments = request.POST.get(
                "comments",
                approval.comments
            )

            approval.save()

            if approval.expense:

                approval.expense.status = "APPROVED"
                approval.expense.save()

            if approval.sponsorship:

                approval.sponsorship.status = "APPROVED"
                approval.sponsorship.save()

            messages.success(
                request,
                "Approval completed successfully."
            )

        elif action == "reject":

            approval.status = "REJECTED"

            approval.approved_by = (
                request.user.username
                if request.user.is_authenticated
                else "Admin"
            )

            approval.comments = request.POST.get(
                "comments",
                approval.comments
            )

            approval.save()

            if approval.expense:

                approval.expense.status = "REJECTED"
                approval.expense.save()

            if approval.sponsorship:

                approval.sponsorship.status = "REJECTED"
                approval.sponsorship.save()

            messages.warning(
                request,
                "Request rejected."
            )

        return redirect(
            "approval_dashboard"
        )

    return render(
        request,
        "process_approval.html",
        {
            "approval": approval
        }
    )

def reminders(request):

    form = ReminderForm(
        request.POST or None
    )

    if request.method == "POST" and form.is_valid():

        reminder = form.save()

        messages.success(
            request,
            "Reminder created successfully."
        )

        return redirect(
            "reminders"
        )

    reminder_list = Reminder.objects.order_by(
        "reminder_date"
    )

    return render(
        request,
        "reminders.html",
        {
            "form": form,
            "reminders": reminder_list
        }
    )

def mark_reminder_sent(request, reminder_id):

    reminder = get_object_or_404(
        Reminder,
        id=reminder_id
    )

    reminder.is_sent = True
    reminder.save()

    Notification.objects.create(
        recipient_type="Participant",
        recipient=reminder.recipient,
        message=reminder.message,
        sent=True
    )

    messages.success(
        request,
        "Reminder marked as sent."
    )

    return redirect(
        "reminders"
    )


def api_events(request):

    events = Event.objects.select_related(
        "venue"
    ).all()

    data = []

    for event in events:

        data.append({
            "id": event.id,
            "name": event.name,
            "event_type": event.event_type,
            "date": str(event.date),
            "budget": str(event.budget),
            "expected_participants": event.expected_participants,
            "status": event.status,
            "venue": (
                event.venue.name
                if event.venue
                else None
            ),
        })

    APIActivityLog.objects.create(
        endpoint="/api/events/",
        method=request.method,
        description="Event list API accessed"
    )

    return JsonResponse(
        {
            "success": True,
            "count": len(data),
            "events": data
        }
    )

def api_event_detail(request, event_id):

    event = get_object_or_404(
        Event.objects.select_related("venue"),
        id=event_id
    )

    data = {

        "id": event.id,

        "name": event.name,

        "event_type": event.event_type,

        "date": str(event.date),

        "budget": str(event.budget),

        "expected_participants":
            event.expected_participants,

        "status":
            event.status,

        "venue":
            event.venue.name
            if event.venue
            else None,

        "attendees":
            event.attendees.count(),

        "resources":
            event.resource_allocations.count(),

        "vendors":
            event.vendor_assignments.count(),

        "sponsorships":
            event.sponsorships.count(),
    }

    APIActivityLog.objects.create(
        endpoint=f"/api/events/{event_id}/",
        method=request.method,
        description="Event detail API accessed"
    )

    return JsonResponse({
        "success": True,
        "event": data
    })

def api_finance(request, event_id):

    event = get_object_or_404(
        Event,
        id=event_id
    )

    budget, created = Budget.objects.get_or_create(
        event=event,
        defaults={
            "amount": 0
        }
    )

    paid_expenses = Expense.objects.filter(
        event=event,
        status="PAID"
    )

    approved_expenses = Expense.objects.filter(
        event=event,
        status="APPROVED"
    )

    revenues = Revenue.objects.filter(
        event=event
    )

    total_paid = sum(
        expense.amount
        for expense in paid_expenses
    )

    total_approved = sum(
        expense.amount
        for expense in approved_expenses
    )

    total_revenue = sum(
        revenue.amount
        for revenue in revenues
    )

    return JsonResponse({

        "success": True,

        "event": event.name,

        "budget": str(
            budget.amount
        ),

        "paid_expenses": str(
            total_paid
        ),

        "approved_expenses": str(
            total_approved
        ),

        "revenue": str(
            total_revenue
        ),

        "remaining_budget": str(
            budget.amount - total_paid
        ),

        "profit": str(
            total_revenue - total_paid
        ),
    })

def api_sponsorships(request, event_id):

    event = get_object_or_404(
        Event,
        id=event_id
    )

    sponsors = Sponsorship.objects.filter(
        event=event
    )

    data = []

    for sponsor in sponsors:

        data.append({

            "id": sponsor.id,

            "sponsor":
                sponsor.sponsor_name,

            "type":
                sponsor.sponsorship_type,

            "amount":
                str(sponsor.amount),

            "status":
                sponsor.status,

            "contact":
                sponsor.contact_person,

            "email":
                sponsor.email,
        })

    return JsonResponse({

        "success": True,

        "event":
            event.name,

        "count":
            len(data),

        "sponsorships":
            data
    })

def home(request):
    """
    Public landing page.
    This page is accessible before login.
    """
    return render(request, "home.html")


def about(request):
    """
    About EventSphere page.
    """
    return render(request, "about.html")


def how_it_works(request):
    """
    Explains the EventSphere workflow.
    """
    return render(request, "how_it_works.html")


def features(request):
    """
    Displays the major EventSphere features.
    """
    return render(request, "features.html")