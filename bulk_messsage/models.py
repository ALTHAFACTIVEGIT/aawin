from django.db import models

# Create your models here.


class Department(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=100)
    session = models.CharField(max_length=100)
    time_start = models.CharField(max_length=10)
    time_end = models.CharField(max_length=10)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class Person(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.BigIntegerField(blank=True, null=True)
    department = models.ForeignKey(Department, blank=True, null=True)
    roll_number = models.CharField(max_length=20, blank=True, null=True)


class Group(models.Model):
    name = models.CharField(max_length=100)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class PersonMessage(models.Model):
    group = models.ForeignKey(Group)
    person = models.ForeignKey(Person)
    message = models.TextField()
    response_json = models.TextField(blank=True, null=True)
    response_status_code = models.CharField(max_length=10, blank=True, null=True)
    response_message = models.TextField(blank=True, null=True)
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)



