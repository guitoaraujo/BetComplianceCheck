from django.db import models

class Analysis(models.Model):
    class GlobalStatus(models.TextChoices):
        COMPLIANT = "green", "Compliant"
        ATTENTION = "yellow", "Attention Required"
        NON_COMPLIANT = "red", "Non-Compliant"

    created_at = models.DateTimeField(auto_now_add=True)

    # Uploaded creative
    image = models.ImageField(upload_to="creatives/%Y/%m/%d/")

    # Results
    global_status = models.CharField(
        max_length=10,
        choices=GlobalStatus.choices,
        default=GlobalStatus.ATTENTION,
    )

    # JSON structure: cards, findings, suggestions, etc.
    result_json = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f"Analysis #{self.id} - {self.get_global_status_display()}"
