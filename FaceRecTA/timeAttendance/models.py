from django.db import models

class Departments(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)

class EmployeeDetail(models.Model):
    id = models.CharField(primary_key=True, max_length=500)
    name = models.CharField(max_length=32)
    gender = models.IntegerField()
    image_name = models.CharField(max_length=500)
    department = models.ForeignKey(Departments, default = None, on_delete=models.SET_DEFAULT, null=True)
    branch = models.CharField(max_length=500, null=True)
    status = models.IntegerField()

class TerminalDetails(models.Model):
    terminal_id = models.IntegerField(primary_key=True)
    terminal_ip = models.CharField(max_length=100)
    terminal_name = models.CharField(max_length=100)

class EmployeeAttendance(models.Model):
    capture_time = models.CharField(max_length=200)
    capture_location = models.ForeignKey(TerminalDetails,default=000000 ,on_delete=models.SET_DEFAULT)
    EmployeeDetail = models.ForeignKey(EmployeeDetail, on_delete=models.CASCADE, null=True)
    temperature = models.CharField(max_length=100, default='')

class StrangerDetails(models.Model):
    capture_time = models.CharField(max_length=200)
    capture_location = models.ForeignKey(TerminalDetails,default=000000 ,on_delete=models.SET_DEFAULT)
    temperature = models.CharField(max_length=100, default='')
    image_name = models.CharField(max_length=500)