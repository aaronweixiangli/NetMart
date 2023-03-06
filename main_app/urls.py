from django.urls import path
from . import views
	
urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/signup/', views.signup, name='signup'),
    path('about/', views.about, name='about'),
    path('about/team', views.about_team, name='about_team'),
    path('products/', views.products_index, name='products_index'),
    path('products/<str:tcin>', views.products_detail, name='products_detail'),
    path('accounts/buying/pending', views.buying_pending, name='buying_pending'),
    path('accounts/buying/history', views.buying_history, name='buying_history'),
    path('accounts/selling/listing', views.selling_listing, name='selling_listing'),
    path('accounts/selling/pending', views.selling_pending, name='selling_pending'),
    path('accounts/selling/history', views.selling_history, name='selling_history'),
]