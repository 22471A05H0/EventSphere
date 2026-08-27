from django import forms
from .models import Event,Venue,Resource,Attendee,Vendor,VendorAssignment,Notification,Budget, Expense, Revenue

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