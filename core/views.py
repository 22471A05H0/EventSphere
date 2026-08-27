from io import BytesIO
import qrcode
from django.contrib import messages
from django.core.files.base import ContentFile
from django.db.models import Count,Sum
from django.shortcuts import get_object_or_404,redirect,render
from .models import Event,Venue,Resource,ResourceAllocation,Attendee,Ticket,Vendor,VendorAssignment,Notification,Budget, Expense, Revenue
from .forms import EventForm,VenueForm,ResourceForm,AttendeeForm,VendorForm,AllocationForm,AssignmentForm,RatingForm,NotificationForm,BudgetForm, ExpenseForm, RevenueForm


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