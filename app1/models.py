from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Add custom fields
    UserID = models.AutoField(primary_key=True)
    ApprovalStatus = models.BooleanField(default=False)
    IsAdmin = models.BooleanField(default=False)
    
    
class DeviceType(models.Model):
    DeviceTypeID = models.AutoField(primary_key=True)
    TypeName = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.TypeName

class CPU(models.Model):
    Brand = models.CharField(max_length=100)
    Model = models.CharField(max_length=100)
    ClockSpeed = models.FloatField()
    Cores = models.IntegerField()

    def __str__(self):
        return f"{self.Brand} {self.Model}"

class GPU(models.Model):
    Brand = models.CharField(max_length=100)
    Model = models.CharField(max_length=100)
    VRAM = models.IntegerField()

    def __str__(self):
        return f"{self.Brand} {self.Model}"

class RAM(models.Model):
    Capacity = models.IntegerField()
    Type = models.CharField(max_length=100)
    Speed = models.IntegerField()

    def __str__(self):
        return f"{self.Capacity} GB {self.Type} RAM"



class Equipment(models.Model):
    EquipmentID = models.AutoField(primary_key=True)
    DeviceName = models.CharField(max_length=100)
    DeviceTypeID = models.ForeignKey(DeviceType, on_delete=models.CASCADE)
    DeviceSerial = models.CharField(max_length=50)
    IsOnsiteOnly = models.BooleanField(default=False)
    CPUID = models.ForeignKey(CPU, on_delete=models.CASCADE)
    GPUID = models.ForeignKey(GPU, on_delete=models.CASCADE)
    RAMID = models.ForeignKey(RAM, on_delete=models.CASCADE)
    Availability = models.BooleanField(default=True)

    def __str__(self):
        return self.DeviceName



class Booking(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    booking_date = models.DateField() 
    return_date = models.DateField(null=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Returned', 'Returned'),
        ('Cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    ALERT_STATUS_CHOICES = [
        ('No Alert', 'No Alert'),
        ('Reminder Sent', 'Reminder Sent'),
        ('Overdue', 'Overdue'),
    ]
    alert_status = models.CharField(max_length=20, choices=ALERT_STATUS_CHOICES, default='No Alert')
    
    ADMIN_APPROVAL_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    admin_approval = models.CharField(max_length=20, choices=ADMIN_APPROVAL_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.user.username} - {self.equipment.DeviceName} - Booking: {self.booking_date}, Return: {self.return_date}"


class InventoryCount(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    equipment = models.OneToOneField(Equipment, on_delete=models.CASCADE, primary_key=True)
    count_date = models.DateField(auto_now_add=True)  # Set automatically to current date when object is created
    quantity = models.IntegerField()

    def __str__(self):
        return f"User: {self.user.username}, Equipment: {self.equipment.DeviceName}, Count Date: {self.count_date}, Quantity: {self.quantity}"





class DeviceAudit(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    audit_date = models.DateField(auto_now_add=True)  # Set automatically to current date when object is created
    AUDIT_STATUS_CHOICES = [
        ('Completed', 'Completed'),
        ('Pending', 'Pending'),
    ]
    audit_status = models.CharField(max_length=20, choices=AUDIT_STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Equipment ID: {self.equipment_id}, Audit Date: {self.audit_date}, Audit Status: {self.audit_status}"

class Report(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=100)
    report_date = models.DateField(auto_now_add=True)  # Set automatically to current date when object is created

    def __str__(self):
        return f"User: {self.user.username}, Report Type: {self.report_type}, Report Date: {self.report_date}"