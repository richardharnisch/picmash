from django.db import models

class ImageEntry(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='contest_images/')
    score = models.IntegerField(default=0)   # you can keep “score” if you still want it, or remove it
    rating = models.FloatField(default=1500)  # Elo rating, start at 1500

    def __str__(self):
        return f"{self.name} (Rating: {self.rating:.0f})"
