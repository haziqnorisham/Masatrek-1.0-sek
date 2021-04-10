from django.db import models
from timeAttendance.models import TerminalDetails

class GuestDetails(models.Model):
    name = models.CharField(max_length=500, null=False)
    image_name = models.CharField(max_length=500, null=False)
    phone_number = models.IntegerField(null=False)
    nric = models.IntegerField(null=False, unique=True)
    comment = models.CharField(max_length=500, null=True)
    valid_until = models.CharField(max_length=200, default='0')
    status = models.IntegerField()

class GuestAttendance(models.Model):
    capture_time = models.CharField(max_length=200)
    capture_location = models.ForeignKey(TerminalDetails,default=000000 ,on_delete=models.SET_DEFAULT)
    GuestDetails = models.ForeignKey(GuestDetails, on_delete=models.CASCADE, null=True)
    temperature = models.CharField(max_length=100, default='')

class GuestBlacklist(models.Model):
    capture_time = models.CharField(max_length = 200)
    capture_location = models.ForeignKey(TerminalDetails,default=000000 ,on_delete=models.SET_DEFAULT)
    GuestDetails = models.ForeignKey(GuestDetails, on_delete=models.CASCADE, null=True)
    temperature = models.CharField(max_length=100, default='')
