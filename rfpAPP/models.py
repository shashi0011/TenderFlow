from django.db import models
from django.contrib.auth.models import AbstractUser


# USER

class User(AbstractUser):
    ROLE_CHOICES = (("admin", "Admin"),("vendor", "Vendor"),)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="vendor")

    def __str__(self):
        return self.username



# Vendor profile
class VendorProfile(models.Model):
    STATUS_CHOICES = (("pending", "Pending"),("approved", "Approved"),("rejected", "Rejected"),)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    gst_number = models.CharField(max_length=20)
    pan_number = models.CharField(max_length=10)
    annual_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    no_of_employees = models.PositiveIntegerField()
    categories = models.ManyToManyField("Category")
    def __str__(self):
        return self.company_name


# Category
class Category(models.Model):
    name = models.CharField(max_length=100)


    def __str__(self):
        return self.name

# Rfp
class RFP(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    item_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()

    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    max_price = models.DecimalField(max_digits=10, decimal_places=2)

    last_date = models.DateField()

    def __str__(self):
        return self.title


# Rfp vendor

class RFPVendor(models.Model):
    STATUS_CHOICES = (
        ("open", "Open"),
        ("closed", "Closed"),
    )

    rfp = models.ForeignKey(RFP, on_delete=models.CASCADE)
    vendor = models.ForeignKey(User, on_delete=models.CASCADE)
    reply_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open")

    class Meta:
        unique_together = ("rfp", "vendor")

    def __str__(self):
        return f"{self.rfp.title} - {self.vendor.username}"


# Quote

class Quote(models.Model):
    rfp_vendor = models.OneToOneField(RFPVendor, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.rfp_vendor.vendor.username} - {self.price}"