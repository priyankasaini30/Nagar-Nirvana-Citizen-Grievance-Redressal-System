from django import forms
from .models import Complaint, Category, Feedback

from .models import Category

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = [
            'title',
            'category',
            'description',
            'priority',
            'attachment',
            'location'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['resolution_status', 'rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'resolution_status': 'Resolution confirmation',
            'rating': 'Rating (optional)',
            'comment': 'Comments (optional)',
        }
