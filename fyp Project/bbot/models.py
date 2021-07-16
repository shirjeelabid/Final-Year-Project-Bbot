from django.db import models

# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length=200)
    img = models.ImageField(upload_to='pics')
    description = models.TextField()
    date = models.DateField()
    price = models.IntegerField()
    deadline = models.DateField()
    thresh = models.IntegerField( default=100)

class Customer(models.Model):
    id = models.AutoField (primary_key=True)

class DealDone(models.Model):
    price = models.IntegerField()
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)