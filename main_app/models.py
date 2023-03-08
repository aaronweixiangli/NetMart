from django.db import models
from django.urls import reverse
from datetime import date
from django.contrib.auth.models import User

class BuyOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user.username}'s Buy Order"

class SalesOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user.username}'s Sales Order"

class SellerReview(models.Model):
    rating = models.IntegerField()
    review = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"Review of {self.user.username}: Rating {self.rating}, {self.review}"

class WishList(models.Model):
    product = models.ManyToManyField('Product')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user.username}'s Wish List"

class Item(models.Model):
    tcin = models.CharField(max_length=100)
    title = models.CharField(max_length=300)
    brand = models.CharField(max_length=100)
    sell_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    date_created = models.DateField()
    date_sold = models.DateField(null=True, blank=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    item_description = models.TextField()
    buy_order = models.ForeignKey(BuyOrder, on_delete=models.CASCADE, null=True, blank=True)
    sell_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, null=True, blank=True)
    seller_rating = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    seller_review = models.ForeignKey(SellerReview, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    def __str__(self):
        return f"Item Title:{self.title}; Seller:{self.seller.username}; Tcin:{self.tcin}"
    class Meta:
        ordering = ['-date_created']

class ItemPhoto(models.Model):
    url = models.TextField()
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    def __str__(self):
        return f"Photo for item_id: {self.item_id} @{self.url}"

class Product(models.Model):
    tcin = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    main_image = models.TextField()
    def __str__(self):
        return f"Product Title:{self.title}; Tcin:{self.tcin}"

class ProductFeature(models.Model):
    description = models.TextField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    def __str__(self):
        return f"Feature for {self.product.title} with tcin:{self.product.tcin}"