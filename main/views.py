from django.shortcuts import render, redirect
from main.forms import ProductEntryForm
from main.models import Product
from django.http import HttpResponse
from django.core import serializers
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags
import json
from django.http import JsonResponse

@login_required(login_url='/login')
def show_main(request):

    context = {
        'name': request.user.username,
        'class': 'PBP C',
        'last_login': request.COOKIES['last_login'],
    }

    return render(request, "main.html", context)

def create_product_entry(request):
    form = ProductEntryForm(request.POST or None)

    if form.is_valid() and request.method == "POST":
        product_entry = form.save(commit=False)
        product_entry.user = request.user
        product_entry.save()
        return redirect('main:show_main')

    context = {'form': form}
    return render(request, "create_product_entry.html", context)

def show_xml(request):
    data = Product.objects.filter(user=request.user)
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

def show_json(request):
    data = Product.objects.filter(user=request.user)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def show_xml_by_id(request, id):
    data = Product.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

def show_json_by_id(request, id):
    data = Product.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('main:login')
    context = {'form':form}
    return render(request, 'register.html', context)

def login_user(request):
   if request.method == 'POST':
      form = AuthenticationForm(data=request.POST)

      if form.is_valid():
            user = form.get_user()
            login(request, user)
            response = HttpResponseRedirect(reverse("main:show_main"))
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response
      else:
          messages.error(request, "Invalid username or password. Please try again.")
   else:
      form = AuthenticationForm(request)
   context = {'form': form}
   return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
    return response

def edit_product(request, id):
    # Get product entry berdasarkan id
    product = Product.objects.get(pk = id)

    # Set product entry sebagai instance dari form
    form = ProductEntryForm(request.POST or None, instance=product)

    if form.is_valid() and request.method == "POST":
        # Simpan form dan kembali ke halaman awal
        form.save()
        return HttpResponseRedirect(reverse('main:show_main'))

    context = {'form': form}
    return render(request, "edit_product.html", context)

def delete_product(request, id):
    # Get product berdasarkan id
    product = Product.objects.get(pk = id)
    # Hapus product
    product.delete()
    # Kembali ke halaman awal
    return HttpResponseRedirect(reverse('main:show_main'))

@csrf_exempt
@require_POST
def add_product_entry_ajax(request):
    name = strip_tags(request.POST.get("name"))
    price = strip_tags(request.POST.get("price"))
    description = strip_tags(request.POST.get("description"))
    stock = strip_tags(request.POST.get("stock"))
    rating = request.POST.get("rating")
    user = request.user

    new_product = Product(
        name=name, price=price,
        description=description,
        stock=stock, rating=rating,
        user=user
    )
    
    form = ProductEntryForm(request.POST, instance=new_product)
    if form.is_valid():
        new_product.save()
        return HttpResponse(b"CREATED", status=201)
    else:
        print(form.errors)
        errors = form.errors.as_json()
        return HttpResponse(errors, status=400, content_type="application/json")
    
@csrf_exempt
def create_product_flutter(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        new_product = Product.objects.create(
            user=request.user,
            name=data["name"],
            description=data["description"],
            stock=int(data["stock"]),
            price=int(data["price"]),
            rating=float(data["rating"]),
        )

        new_product.save()

        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"status": "error"}, status=401)