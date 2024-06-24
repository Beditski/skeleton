from django.db import models

class UserFile(models.Model):
    file_path = models.TextField()
    file_name = models.TextField()

    def __str__(self):
        return self.id
