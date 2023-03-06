from django.contrib import admin
from .models import BuyOrder, SalesOrder, SellerReview, WishList, Item, ItemPhoto, Product, ProductFeature 

admin.site.register(BuyOrder)
admin.site.register(SalesOrder)
admin.site.register(SellerReview)
admin.site.register(WishList)
admin.site.register(Item)
admin.site.register(ItemPhoto)
admin.site.register(Product)
admin.site.register(ProductFeature)