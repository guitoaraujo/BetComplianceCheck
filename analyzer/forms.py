from django import forms
from .models import Analysis

class AnalysisUploadForm(forms.ModelForm):
    class Meta:
        model = Analysis
        fields = ["image"]

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not image:
            raise forms.ValidationError("Please upload an image.")

        valid_content_types = {"image/jpeg", "image/png", "image/webp"}
        if hasattr(image, "content_type") and image.content_type not in valid_content_types:
            raise forms.ValidationError("Only JPG, PNG or WEBP images are allowed.")

        max_mb = 8
        if image.size > max_mb * 1024 * 1024:
            raise forms.ValidationError(f"Image too large. Max {max_mb}MB.")

        return image
