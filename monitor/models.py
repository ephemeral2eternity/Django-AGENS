from django.db import models

# The monitoring variables are defined here
class Load(models.Model):
	load = models.IntegerField()
	total = models.IntegerField()
	time = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return str(self.load)

class BW(models.Model):
	tx = models.IntegerField()
	bw = models.DecimalField(max_digits=10, decimal_places=5)
	time = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return str(self.bw)

class RTTS(models.Model):
	rtts = models.CharField(max_length=9999)
	time = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return rtts
