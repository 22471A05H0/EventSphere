from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views


urlpatterns = [


    path('', views.home, name='home'),

    path(
        'about/',
        views.about,
        name='about'
    ),

    path(
        'how-it-works/',
        views.how_it_works,
        name='how_it_works'
    ),

    path(
        'features/',
        views.features,
        name='features'
    ),



    path(
        'accounts/',
        include('accounts.urls')
    ),



    path(
        'admin/',
        admin.site.urls
    ),



    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),

    path(
        'events/create/',
        views.create_event,
        name='create_event'
    ),

    path(
        'events/<int:event_id>/',
        views.event_detail,
        name='event_detail'
    ),

    path(
        'events/<int:event_id>/venue/',
        views.select_venue,
        name='select_venue'
    ),

    path(
        'events/<int:event_id>/resources/',
        views.allocate_resources,
        name='allocate_resources'
    ),

    path(
        'events/<int:event_id>/register/',
        views.register_attendee,
        name='register_attendee'
    ),




    path(
        'tickets/<int:attendee_id>/',
        views.ticket_detail,
        name='ticket_detail'
    ),

    path(
        'checkin/',
        views.checkin,
        name='checkin'
    ),




    path(
        'venues/',
        views.venues,
        name='venues'
    ),

    path(
        'resources/',
        views.resources,
        name='resources'
    ),

    path(
        'vendors/',
        views.vendors,
        name='vendors'
    ),

    path(
        'events/<int:event_id>/vendors/',
        views.assign_vendors,
        name='assign_vendors'
    ),

    path(
        'vendors/<int:vendor_id>/rate/',
        views.rate_vendor,
        name='rate_vendor'
    ),



    path(
        'notifications/',
        views.notifications,
        name='notifications'
    ),

    path(
        'reports/',
        views.reports,
        name='reports'
    ),


    path(
        'events/<int:event_id>/finance/',
        views.finance_dashboard,
        name='finance_dashboard'
    ),

    path(
        'events/<int:event_id>/finance/budget/',
        views.set_budget,
        name='set_budget'
    ),

    path(
        'events/<int:event_id>/finance/expense/add/',
        views.add_expense,
        name='add_expense'
    ),

    path(
        'events/<int:event_id>/finance/revenue/add/',
        views.add_revenue,
        name='add_revenue'
    ),




    path(
        'events/<int:event_id>/sponsorships/',
        views.sponsorships,
        name='sponsorships'
    ),

    path(
        'sponsorships/<int:sponsorship_id>/approve/',
        views.approve_sponsorship,
        name='approve_sponsorship'
    ),



    path(
        'approvals/',
        views.approval_dashboard,
        name='approval_dashboard'
    ),

    path(
        'approvals/<int:approval_id>/process/',
        views.process_approval,
        name='process_approval'
    ),

    path(
        'expenses/<int:expense_id>/request-approval/',
        views.request_expense_approval,
        name='request_expense_approval'
    ),


    path(
        'reminders/',
        views.reminders,
        name='reminders'
    ),

    path(
        'reminders/<int:reminder_id>/sent/',
        views.mark_reminder_sent,
        name='mark_reminder_sent'
    ),



    path(
        'api/events/',
        views.api_events,
        name='api_events'
    ),

    path(
        'api/events/<int:event_id>/',
        views.api_event_detail,
        name='api_event_detail'
    ),

    path(
        'api/events/<int:event_id>/finance/',
        views.api_finance,
        name='api_finance'
    ),

    path(
        'api/events/<int:event_id>/sponsorships/',
        views.api_sponsorships,
        name='api_sponsorships'
    ),
]


urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)