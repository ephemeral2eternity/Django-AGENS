from django.db import models

# Save all the cache servers in overlay.Server model
class Server(models.Model):
	name = models.CharField(max_length=20)
	ip = models.CharField(max_length=20)
	rtt = models.DecimalField(max_digits=10, decimal_places=3, default=255.0)
	isLocal = models.BooleanField(default=False)
	def __str__(self):
		self.name

class Peer(models.Model):
	name = models.CharField(max_length=20)
	ip = models.CharField(max_length=20)
	def __str__(self):
		self.name
