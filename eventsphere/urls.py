from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views
from django.urls import include
urlpatterns=[path("accounts/", include("accounts.urls")),
             path('admin/',admin.site.urls),
             path('',views.dashboard,name='dashboard'),
             path('events/create/',views.create_event,name='create_event'),
             path('events/<int:event_id>/',views.event_detail,name='event_detail'),
             path('events/<int:event_id>/venue/',views.select_venue,name='select_venue'),
             path('events/<int:event_id>/resources/',views.allocate_resources,name='allocate_resources'),
             path('events/<int:event_id>/register/',views.register_attendee,name='register_attendee'),
             path('tickets/<int:attendee_id>/',views.ticket_detail,name='ticket_detail'),
             path('checkin/',views.checkin,name='checkin'),
             path('venues/',views.venues,name='venues'),
             path('resources/',views.resources,name='resources'),
             path('vendors/',views.vendors,name='vendors'),
             path('events/<int:event_id>/vendors/',views.assign_vendors,name='assign_vendors'),
             path('vendors/<int:vendor_id>/rate/',views.rate_vendor,name='rate_vendor'),
             path('notifications/',views.notifications,name='notifications'),
             path('reports/',views.reports,name='reports')]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
urlpatterns+=[

    path(
        "events/<int:event_id>/finance/",
        views.finance_dashboard,
        name="finance_dashboard"
    ),

    path(
        "events/<int:event_id>/finance/budget/",
        views.set_budget,
        name="set_budget"
    ),

    path(
        "events/<int:event_id>/finance/expense/add/",
        views.add_expense,
        name="add_expense"
    ),

    path(
        "events/<int:event_id>/finance/revenue/add/",
        views.add_revenue,
        name="add_revenue"
    ),
]
