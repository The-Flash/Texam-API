from django import forms

from .models import Test

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = (
            "test_id",
            "name",
            "submission_time",
            "allow_late_submission",
            "description"
        )