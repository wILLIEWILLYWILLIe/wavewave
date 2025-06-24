from django.db import models

# Create your models here.
class DashboardData(models.Model):
    topic_name = models.TextField()
    json_data = models.JSONField() 
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.updated_at