from django import forms
from .models import Event,Venue,Resource,Attendee,Vendor,VendorAssignment,Notification,Budget, Expense, Revenue,Sponsorship, Approval, Reminder

class EventForm(forms.ModelForm):
    class Meta:
        model=Event; fields=['name','event_type','date','budget','expected_participants']
        widgets={'date':forms.DateInput(attrs={'type':'date'})}
class VenueForm(forms.ModelForm):
    class Meta: model=Venue; fields=['name','location','capacity','available']
class ResourceForm(forms.ModelForm):
    class Meta: model=Resource; fields=['name','total_quantity','available_quantity']
class AttendeeForm(forms.ModelForm):
    class Meta: model=Attendee; fields=['name','email','phone','college','department']
    def clean_phone(self):
        p=self.cleaned_data['phone']
        if not p.isdigit() or len(p)!=10: raise forms.ValidationError('Phone must contain exactly 10 digits.')
        return p
class VendorForm(forms.ModelForm):
    class Meta: model=Vendor; fields=['name','service_type','phone','email','availability']
    def clean_phone(self):
        p=self.cleaned_data['phone']
        if not p.isdigit() or len(p)!=10: raise forms.ValidationError('Phone must contain exactly 10 digits.')
        return p
class AllocationForm(forms.Form):
    resource=forms.ModelChoiceField(queryset=Resource.objects.none())
    quantity=forms.IntegerField(min_value=1)
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs); self.fields['resource'].queryset=Resource.objects.filter(available_quantity__gt=0)
class AssignmentForm(forms.ModelForm):
    class Meta: model=VendorAssignment; fields=['vendor','service']
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs); self.fields['vendor'].queryset=Vendor.objects.filter(availability=True)
class RatingForm(forms.ModelForm):
    class Meta:
        model=Vendor; fields=['quality','timeliness','cost_rating','communication']
        widgets={x:forms.NumberInput(attrs={'min':1,'max':5}) for x in ['quality','timeliness','cost_rating','communication']}
class NotificationForm(forms.ModelForm):
    class Meta: model=Notification; fields=['recipient_type','recipient','message']

class BudgetForm(forms.ModelForm):

    class Meta:
        model = Budget
        fields = ["amount"]

        widgets = {
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter budget"
                }
            )
        }


class ExpenseForm(forms.ModelForm):

    class Meta:
        model = Expense

        fields = [
            "category",
            "description",
            "amount",
            "status",
            "payment_method",
            "invoice_number",
        ]

        widgets = {
            "category": forms.Select(
                attrs={"class": "form-control"}
            ),

            "description": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "amount": forms.NumberInput(
                attrs={"class": "form-control"}
            ),

            "status": forms.Select(
                attrs={"class": "form-control"}
            ),

            "payment_method": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "invoice_number": forms.TextInput(
                attrs={"class": "form-control"}
            ),
        }


class RevenueForm(forms.ModelForm):

    class Meta:
        model = Revenue

        fields = [
            "source",
            "description",
            "amount",
            "payment_method",
        ]

        widgets = {
            "source": forms.Select(
                attrs={"class": "form-control"}
            ),

            "description": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "amount": forms.NumberInput(
                attrs={"class": "form-control"}
            ),

            "payment_method": forms.TextInput(
                attrs={"class": "form-control"}
            ),
        }

class SponsorshipForm(forms.ModelForm):

    class Meta:

        model = Sponsorship

        fields = [
            "sponsor_name",
            "contact_person",
            "email",
            "phone",
            "sponsorship_type",
            "amount",
            "status",
            "benefits",
        ]

        widgets = {

            "sponsor_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Sponsor company name"
                }
            ),

            "contact_person": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "sponsorship_type": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0"
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "benefits": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Sponsor benefits"
                }
            ),
        }

    def clean_phone(self):

        phone = self.cleaned_data["phone"]

        if not phone.isdigit() or len(phone) != 10:
            raise forms.ValidationError(
                "Phone must contain exactly 10 digits."
            )

        return phone


class ApprovalForm(forms.ModelForm):

    class Meta:

        model = Approval

        fields = [
            "approval_type",
            "comments",
        ]

        widgets = {

            "approval_type": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "comments": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Approval comments"
                }
            ),
        }


class ReminderForm(forms.ModelForm):

    class Meta:

        model = Reminder

        fields = [
            "reminder_type",
            "title",
            "message",
            "reminder_date",
            "recipient",
        ]

        widgets = {

            "reminder_type": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Reminder title"
                }
            ),

            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4
                }
            ),

            "reminder_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local"
                }
            ),

            "recipient": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Email or recipient"
                }
            ),
        }