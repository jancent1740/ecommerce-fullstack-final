from django.shortcuts import render, redirect
from .models import Product, Category, Profile
from payment.models import Order, OrderItem
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm

from payment.forms import ShippingForm
from payment.models import ShippingAddress

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .models import Product, Order
from .utils import get_customer_for_user

from django import forms
from django.db.models import Q
import json
from cart.cart import Cart

import requests
from django.shortcuts import render
from django.http import JsonResponse

from django.http import JsonResponse
from django.db.models import Sum, F
from store.models import Product

def search(request):
	# Determine if they filled out the form
	if request.method == "POST":
		searched = request.POST['searched']
		# Query The Products DB Model
		searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
		# Test for null
		if not searched:
			messages.success(request, "That Product Does Not Exist...Please try Again.")
			return render(request, "search.html", {})
		else:
			return render(request, "search.html", {'searched':searched})
	else:
		return render(request, "search.html", {})	


def update_info(request):
	if request.user.is_authenticated:
		# Get Current User
		current_user = Profile.objects.get(user__id=request.user.id)
		# Get Current User's Shipping Info
		shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
		
		# Get original User Form
		form = UserInfoForm(request.POST or None, instance=current_user)
		# Get User's Shipping Form
		shipping_form = ShippingForm(request.POST or None, instance=shipping_user)		
		if form.is_valid() or shipping_form.is_valid():
			# Save original form
			form.save()
			# Save shipping form
			shipping_form.save()

			messages.success(request, "Your Info Has Been Updated!!")
			return redirect('home')
		return render(request, "update_info.html", {'form':form, 'shipping_form':shipping_form})
	else:
		messages.success(request, "You Must Be Logged In To Access That Page!!")
		return redirect('home')



def update_password(request):
	if request.user.is_authenticated:
		current_user = request.user
		# Did they fill out the form
		if request.method  == 'POST':
			form = ChangePasswordForm(current_user, request.POST)
			# Is the form valid
			if form.is_valid():
				form.save()
				messages.success(request, "Your Password Has Been Updated...")
				login(request, current_user)
				return redirect('update_user')
			else:
				for error in list(form.errors.values()):
					messages.error(request, error)
					return redirect('update_password')
		else:
			form = ChangePasswordForm(current_user)
			return render(request, "update_password.html", {'form':form})
	else:
		messages.success(request, "You Must Be Logged In To View That Page...")
		return redirect('home')
def update_user(request):
	if request.user.is_authenticated:
		current_user = User.objects.get(id=request.user.id)
		user_form = UpdateUserForm(request.POST or None, instance=current_user)

		if user_form.is_valid():
			user_form.save()

			login(request, current_user)
			messages.success(request, "User Has Been Updated!!")
			return redirect('home')
		return render(request, "update_user.html", {'user_form':user_form})
	else:
		messages.success(request, "You Must Be Logged In To Access That Page!!")
		return redirect('home')


def category_summary(request):
    # Hardcode categories with images
    categories = [
        {"name": "Katana", "img": "Katana.png"},
        {"name": "Bow", "img": "Bow.webp"},
        {"name": "Cannon", "img": "Cannon.webp"},
        {"name": "Chackram", "img": "Chakram.webp"},
        {"name": "Cross", "img": "Cross.webp"},
        {"name": "Gauntlet", "img": "Gauntlet.webp"},
        {"name": "Greatsword", "img": "Greatsword.webp"},
        {"name": "Lance", "img": "Lance.webp"},
        {"name": "Pistol", "img": "Pistol.png"},
        {"name": "Scythe", "img": "Scythe.webp"},
    ]
    return render(request, "category_summary.html", {"categories": categories})


def category(request, foo):
	# Replace Hyphens with Spaces
	foo = foo.replace('-', ' ')
	# Grab the category from the url
	try:
		# Look Up The Category
		category = Category.objects.get(name=foo)
		products = Product.objects.filter(category=category)
		return render(request, 'category.html', {'products':products, 'category':category})
	except:
		messages.success(request, ("That Category Doesn't Exist..."))
		return redirect('home')


def product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    quantity_range = range(1, 6)  # 1 to 5 for the dropdown
    context = {
        'product': product,
        'quantity_range': quantity_range,
    }
    return render(request, 'product.html', context)

def home(request):
	products = Product.objects.all()
	return render(request, 'home.html', {'products':products})


def about(request):
	return render(request, 'about.html', {})	

def login_user(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)

			# Do some shopping cart stuff
			current_user = Profile.objects.get(user__id=request.user.id)
			# Get their saved cart from database
			saved_cart = current_user.old_cart
			# Convert database string to python dictionary
			if saved_cart:
				# Convert to dictionary using JSON
				converted_cart = json.loads(saved_cart)
				# Add the loaded cart dictionary to our session
				# Get the cart
				cart = Cart(request)
				# Loop thru the cart and add the items from the database
				for key,value in converted_cart.items():
					cart.db_add(product=key, quantity=value)

			messages.success(request, ("You Have Been Logged In!"))
			return redirect('home')
		else:
			messages.success(request, ("There was an error, please try again..."))
			return redirect('login')

	else:
		return render(request, 'login.html', {})


def logout_user(request):
	logout(request)
	messages.success(request, ("You have been logged out...Thanks for stopping by..."))
	return redirect('home')



def register_user(request):
	form = SignUpForm()
	if request.method == "POST":
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			# log in user
			user = authenticate(username=username, password=password)
			login(request, user)
			messages.success(request, ("Username Created - Please Fill Out Your User Info Below..."))
			return redirect('update_info')
		else:
			messages.success(request, ("Whoops! There was a problem Registering, please try again..."))
			return redirect('register')
	else:
		return render(request, 'register.html', {'form':form})


def api_product_list(request):
    products = list(Product.objects.values())
    return JsonResponse(products, safe=False)

@login_required
def place_order(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    customer = get_customer_for_user(request.user)
    if not customer:
        # should not happen because of @login_required, but safe guard
        return redirect('login')

    qty = int(request.POST.get("quantity", 1)) if request.method == "POST" else 1
    address = request.POST.get("address", customer.email) or ""
    phone = request.POST.get("phone", customer.phone or "")

    order = Order.objects.create(
        product=product,
        customer=customer,
        quantity=qty,
        address=address,
        phone=phone,
        status=True
    )
    return redirect("order_success")


def api_placed_orders(request):
    """
    Returns JSON list of placed orders.
    """
    from payment.models import Order, OrderItem  # Import the correct models

    orders = Order.objects.all().order_by('-date_ordered')
    data = []
    for order in orders:
        # Get order items for this order
        items = OrderItem.objects.filter(order=order)
        for item in items:
            data.append({
                "id": order.id,
                "product_id": item.product.id if item.product else None,
                "product_name": item.product.name if item.product else None,
                "customer_id": order.user.id if order.user else None,
                "customer_email": order.email,
                "quantity": item.quantity,
                "address": order.shipping_address,
                "phone": getattr(order, 'phone', ''),  # Order model doesn't have phone
                "date": order.date_ordered.isoformat(),
            })
    return JsonResponse(data, safe=False)


def api_total_revenue_by_category(request):
    """
    Returns total revenue grouped by product category.
    Revenue = quantity * price for each order item.
    """
    # Calculate total revenue per category
    revenue_data = (
        OrderItem.objects
        .select_related('product', 'product__category')
        .values('product__category__id', 'product__category__name')
        .annotate(
            total_revenue=Sum(F('quantity') * F('price'))
        )
        .order_by('-total_revenue')
    )

    # Format response
    results = []
    for item in revenue_data:
        results.append({
            "total_revenue": float(item['total_revenue']) if item['total_revenue'] else 0.0,
            "category_id": item['product__category__id'],
            "category_name": item['product__category__name']
        })

    return JsonResponse(results, safe=False)

def api_highest_selling_product(request):
    """
    Returns the product with highest total quantity sold.
    """
    # Get product with highest total quantity
    top_product = (
        OrderItem.objects
        .values('product_id', 'product__name')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')
        .first()
    )

    if top_product:
        result = {
            "total_quantity": top_product['total_quantity'],
            "product_id": top_product['product_id'],
            "product_name": top_product['product__name']
        }
    else:
        result = {
            "total_quantity": 0,
            "product_id": None,
            "product_name": None
        }

    return JsonResponse(result)

def api_least_desirable_product(request):
    """
    Returns the product with lowest total quantity sold.
    Excludes products that have never been sold.
    """
    # Get product with lowest total quantity (but at least 1 sale)
    least_product = (
        OrderItem.objects
        .values('product_id', 'product__name')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('total_quantity')  # Ascending order (lowest first)
        .first()
    )

    if least_product:
        result = {
            "total_quantity": least_product['total_quantity'],
            "product_id": least_product['product_id'],
            "product_name": least_product['product__name']
        }
    else:
        result = {
            "total_quantity": 0,
            "product_id": None,
            "product_name": None
        }

    return JsonResponse(result)