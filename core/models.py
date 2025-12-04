from django.db import models
from django.utils import timezone


class Patient(models.Model):
	GENDER_CHOICES = [
		("M", "Male"),
		("F", "Female"),
		("O", "Other"),
	]

	name = models.CharField(max_length=255)
	age = models.PositiveIntegerField()
	gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
	image1 = models.ImageField(upload_to="patients/", null=True, blank=True)
	image2 = models.ImageField(upload_to="patients/", null=True, blank=True)
	prediction = models.CharField(max_length=255, null=True, blank=True)
	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"{self.name} ({self.created_at.date()})"

# Create your models here.
