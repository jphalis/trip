from django import forms

# Create forms here.


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={"placeholder": "Name"})
    )
    company = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={"placeholder": "Company"}),
        required=False
    )
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={"placeholder": "Email"})
    )
    message = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(
            attrs={"placeholder": "How may we help you?",
                   "style": "height: 7em;"})
    )

    def clean_email(self):
        return self.cleaned_data['email'].lower()
