import uuid
import boto3
import os
import requests
import json
import math
from datetime import date
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

def about_technology(request):
  return render(request, 'about_technology.html')

def signup(request):
  error_message = ''
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      # Save the user to the db
      user = form.save()
      # Automatically log in the new user
      login(request, user)
      # create a BuyOrder and a SalesOrder instance for this user once sign up
      buy_order = BuyOrder.objects.create(user=user)
      sales_order = SalesOrder.objects.create(user=user)
      buy_order.save()
      sales_order.save()
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
        tcin = product_api['tcin'],
        title = product_api['title'],
        brand = product_api['brand'],
        price = product_api['buybox_winner']['price']['value'],
        main_image = product_api['main_image']['link']
    )
    product_db.save()
    features = product_api.get('feature_bullets')
    if features:
      # Create ProductFeature instances for this product_db
      for feature in product_api['feature_bullets']:
        product_feature = ProductFeature.objects.create(description=feature, product=product_db)
        product_feature.save()
  # render the template with the product instance
  return render(request, 'products/detail.html', {'product_api': product_api, 'product_db': product_db})


@login_required
def items_new(request, tcin):
  product = Product.objects.get(tcin=tcin)
  return render(request, 'items/new.html', {'product': product})


@login_required
def items_create(request, tcin):
  product = Product.objects.get(tcin=tcin)
  item = Item.objects.create(
    tcin = tcin,
    title = product.title,
    brand = product.brand,
    sell_price = request.POST.get('sell_price'),
    status = 'listing',
    date_created = date.today(),
    seller = request.user,
    item_description = request.POST.get('item_description'),
    sell_order = SalesOrder.objects.filter(user=request.user).first(),
    product = product
  )
  item.save()
  photo_files = request.FILES.getlist('url')
  print(request.FILES)
  print(photo_files)
  for photo_file in photo_files:
    if photo_file:
      s3 = boto3.client('s3')
      # Need a unique "key" (filename)
      # It needs to keep the same file extension
      # of the file that was uploaded (.png, .jpeg, etc)
      key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
      try:
        bucket = os.environ['S3_BUCKET']
        s3.upload_fileobj(photo_file, bucket, key)
        url = f"{os.environ['S3_BASE_URL']}{bucket}/{key}"
        itemphoto = ItemPhoto.objects.create(url=url, item=item)
        itemphoto.save()
      except Exception as e:
        print('An error occurred uploading file to S3')
        print(e)
  return redirect('products_detail', tcin=tcin)


@login_required
def items_edit(request, id):
  item = Item.objects.get(id=id)
  return render(request, 'items/update.html', {'item':item})


@login_required
def items_update(request, id):
  # update the item instance
  item = Item.objects.get(id=id)
  item.sell_price = request.POST.get('sell_price')
  item.item_description = request.POST.get('item_description')
  item.save()
  # update all item_photo instances that links to this item
  photo_files = request.FILES.getlist('url')
  # if there are photos uploaded, delete existing photos and create new ones
  # otherwise, do nothing
  if photo_files:
    # Delete existing ItemPhotos for this item
    item.itemphoto_set.all().delete()
    for photo_file in photo_files:
      if photo_file:
        s3 = boto3.client('s3')
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        try:
          bucket = os.environ['S3_BUCKET']
          s3.upload_fileobj(photo_file, bucket, key)
          url = f"{os.environ['S3_BASE_URL']}{bucket}/{key}"
          itemphoto = ItemPhoto.objects.create(url=url, item=item)
          itemphoto.save()
        except Exception as e:
          print('An error occurred uploading file to S3')
          print(e)
  return redirect('selling_listing')


class ItemDelete(LoginRequiredMixin, DeleteView):
  model = Item
  success_url = '/accounts/selling/listing'


@login_required
def buying_pending(request):
  return render(request, 'users/buying_pending.html')


@login_required
def buying_history(request):
  return render(request, 'users/buying_history.html')


@login_required
def selling_listing(request):
  sales_order = SalesOrder.objects.filter(user=request.user).first()
  items = Item.objects.filter(sell_order=sales_order, status='listing').all()
  return render(request, 'users/selling_listing.html', {'items': items})


@login_required
def selling_pending(request):
  sales_order = SalesOrder.objects.filter(user=request.user).first()
  items = Item.objects.filter(sell_order=sales_order, status='pending').all()
  return render(request, 'users/selling_pending.html', {'items': items})


@login_required
def selling_history(request):
  sales_order = SalesOrder.objects.filter(user=request.user).first()
  items = Item.objects.filter(sell_order=sales_order, status='complete').all()
  return render(request, 'users/selling_history.html', {'items': items})