import uuid
import boto3
import os
import requests
import json
import math
from urllib.parse import unquote
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import BuyOrder, SalesOrder, SellerReview, WishList, Item, ItemPhoto, Product, ProductFeature 

# Define the home view
def home(request):
  return render(request, 'home.html')

def about(request):
  return render(request, 'about.html')

def about_team(request):
  return render(request, 'about_team.html')

def signup(request):
  error_message = ''
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      # Save the user to the db
      user = form.save()
      # Automatically log in the new user
      login(request, user)
      return redirect('/')
    else:
      error_message = 'Invalid sign up -try again'
  # A bad POST or a GET request, so render signup.html with an empty form
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)

def products_index(request):
  if request.method == 'POST':
    search_term = request.POST['search_term']
    type = request.POST['type']
    sort_by = request.POST['sort_by']
    current_page = int(request.POST['page'])
  elif request.method == 'GET':
    search_term = request.GET['search_term']
    search_term = unquote(search_term)
    type = request.GET['type']
    sort_by = request.GET['sort_by']
    current_page = int(request.GET['page'])
  # set up the request parameters
  params = {
    'api_key': os.environ['API_KEY'],
    'type': type,
    'search_term': search_term,
    'sort_by': sort_by,
    'output': 'json'
  }
  # make the http GET request to RedCircle API
  api_result = requests.get('https://api.redcircleapi.com/request', params).json()
  all_products = api_result['search_results']

  products_per_page = 10
  start_index = (current_page - 1) * products_per_page
  end_index = start_index + products_per_page - 1
  num_of_pages = math.ceil(len(all_products) / products_per_page)
  num_of_pages_list = [x for x in range(1, num_of_pages + 1)]
  products = all_products[start_index:end_index+1]
  #Check if there is a next page
  has_next_page = current_page * products_per_page < len(all_products)
  #Check if there is a previous page
  has_prev_page = current_page > 1

  print(search_term)
  print(type)
  print(sort_by)
  print(current_page)
  return render(request, 'products/index.html', {
    'products': products,
    'search_term': search_term,
    'type': type,
    'sort_by': sort_by,
    'page': current_page,
    'num_of_pages': num_of_pages_list,
    'has_next_page': has_next_page,
    'has_prev_page': has_prev_page
  })


def products_detail(request, tcin):
  params = {
    'api_key': os.environ['API_KEY'],
    'type': 'product',
    'tcin': tcin,
    'output': 'json'
  }
  api_result = requests.get('https://api.redcircleapi.com/request', params).json()
  product_api = api_result['product']
  try:
    # try to retrieve the product instance from the database using the tcin
    product_db = Product.objects.get(tcin=tcin)
  except Product.DoesNotExist:
    # if the product instance does not exist in the database, make the API request and create a new product instance
    product_db = Product.objects.create(
        tcin=product_api['tcin'],
        title=product_api['title'],
        brand=product_api['brand'],
        price=product_api['buybox_winner']['price']['value'],
        main_image=product_api['main_image']['link']
    )
    product_db.save()
    # Create ProductFeature instances for this product_db
    for feature in product_api['feature_bullets']:
      product_feature = ProductFeature.objects.create(description=feature, product=product_db)
      product_feature.save()
  # render the template with the product instance
  return render(request, 'products/detail.html', {'product_api': product_api, 'product_db': product_db})


def buying_pending(request):
  return render(request, 'users/buying_pending.html')


def buying_history(request):
  return render(request, 'users/buying_history.html')


def selling_listing(request):
  return render(request, 'users/selling_listing.html')


def selling_pending(request):
  return render(request, 'users/selling_pending.html')


def selling_history(request):
  return render(request, 'users/selling_history.html')