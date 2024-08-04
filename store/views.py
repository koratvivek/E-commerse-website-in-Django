
import os
from django.conf import settings
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
import requests
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import BidForm
from store.models import Bid, Customer, Products, Order, CartItem, Category
from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator
from decouple import config
# Create your views here.


def Index(request):
    search_query = request.GET.get('search', '')
    ordering_query = request.GET.get('ordering')

    products = Products.objects.all()

    if search_query:
        products = products.filter(name__icontains=search_query)
    if not products.exists():
        products = fetch_all_products_api(search_query)
    if ordering_query == 'price-asd':
        products = products.order_by('price')
    elif ordering_query == 'price-dec':
        products = products.order_by('-price')

    paginator = Paginator(products, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    form = BidForm()
    context = {'product': page_obj, 'search_query': search_query,
               'ordering_query': ordering_query, 'form': form}

    return render(request, 'index.html', context)


def sign_in(request):
    if request.method == "POST":
        firstname = request.POST['firstName']
        lastname = request.POST['lastName']
        email = request.POST['email']
        password = request.POST['password']
        phoneno = request.POST['ph']
        value = {
            'first_name': firstname,
            'last_name': lastname,
            'phone': phoneno,
            'email': email
        }
        error_message = None

        customer = Customer(first_name=firstname,
                            last_name=lastname,
                            phone=phoneno,
                            email=email,
                            password=password)
        error_message = validateCustomer(customer)
        if not error_message:
            print(firstname, lastname, phoneno, email, password)
            customer.password = make_password(customer.password)
            customer.register()
            return redirect('login')
        else:
            data = {
                'error': error_message,
                'values': value
            }
            return render(request, 'signin.html', data)
    return render(request, 'signin.html')


def validateCustomer(customer):
    error_message = None
    if (not customer.first_name):
        error_message = "Please Enter your First Name !!"
    elif len(customer.first_name) < 3:
        error_message = 'First Name must be 3 char long or more'
    elif not customer.last_name:
        error_message = 'Please Enter your Last Name'
    elif len(customer.last_name) < 3:
        error_message = 'Last Name must be 3 char long or more'
    elif not customer.phone:
        error_message = 'Enter your Phone Number'
    elif len(customer.phone) < 10:
        error_message = 'Phone Number must be 10 char Long'
    elif len(customer.password) < 5:
        error_message = 'Password must be 5 char long'
    elif len(customer.email) < 5:
        error_message = 'Email must be 5 char long'
    elif customer.isExists():
        error_message = 'Email Address Already Registered..'

    return error_message


def login(request):
    error_msg = None
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        customer = Customer.get_customer_by_email(email=email)
        if customer:
            flag = check_password(password, customer.password)
            if flag:
                request.session['customer_name'] = customer.first_name
                request.session['customer_id'] = customer.id

                return redirect('home')
            else:
                error_msg = 'Invalid Password'
        else:
            error_msg = 'No record found'
    return render(request, 'login.html', {'error': error_msg})


def logout(request):
    request.session.clear()
    return redirect('home')


def get_customer_from_session(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        customer_id = request.session.get('customer_id')
        if not customer_id:
            return redirect('login')
        customer = get_object_or_404(Customer, id=customer_id)
        request.customer = customer
        return view_func(request, *args, **kwargs)
    return wrapper


@get_customer_from_session
def add_to_cart(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        product=product, user=request.customer, )
    cart_item.save()
    return redirect('cart')


@get_customer_from_session
def update_cart(request):
    if request.method == 'POST':
        for item in CartItem.objects.filter(user=request.customer):
            quantity = request.POST.get(f'quantity_{item.id}')
            if quantity:
                item.quantity = int(quantity)
                item.save()
    return redirect('cart')


@get_customer_from_session
def remove_from_cart(request, product_id):
    cart_item = get_object_or_404(
        CartItem, id=product_id, user=request.customer)
    cart_item.delete()
    return redirect('cart')


@get_customer_from_session
def cart(request):
    cart_items = CartItem.objects.filter(user=request.customer)
    total_price = sum(item.product.price *
                      item.quantity for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})


@get_customer_from_session
def add_order(request):
    address = 'address'
    phone = '1212121212'
    customer = request.customer
    cart_items = CartItem.objects.filter(user=customer)

    if not cart_items.exists():
        return HttpResponse('Cart is empty')

    orders = []

    for item in cart_items:
        order = Order(
            product=item.product,
            customer=customer,
            cart_item_ids=str(item.id),
            quantity=item.quantity,
            price=item.product.price * item.quantity,
            address=address,
            phone=phone,
        )
        order.save()
        orders.append(order)

    return redirect('orders')


@get_customer_from_session
def orders(request):
    orders = Order.objects.filter(customer=request.customer)
    return render(request, 'orders.html', {'orders': orders})


def single_product(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    return render(request, 'product_page.html', {'product': product})


def fetch_all_products_api(product_name):
    url = "https://real-time-amazon-data.p.rapidapi.com/search"
    querystring = {
        "query": f"{product_name}",
        "page": "1",
        "country": "IN",
    }
    headers = {
        "x-rapidapi-key": config('API_KEY'),
        "x-rapidapi-host": config('API_HOST')
    }
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:

        asin = [product['asin']
                for product in response.json()['data']['products']]
        return fetch_single_products(asin)
    return []


def fetch_single_products(asin):
    url = "https://real-time-amazon-data.p.rapidapi.com/product-details"
    headers = {
        "x-rapidapi-key": "9f96066bddmshe4c1a048bc7a19fp1ea4b2jsnb01726ef4ca0",
        "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com"
    }
    products = []
    for i in asin:
        querystring = {"asin": i, "country": "IN"}
        try:
            response = requests.get(url, headers=headers, params=querystring)
            response.raise_for_status()
            response_data = response.json()['data']

            category, created = Category.objects.get_or_create(
                name=response_data['category_path'][0]['name'])
            image_file = download_and_save_image(
                response_data['product_photo'])

            product = Products(
                name=response_data['product_title'],
                price=float(
                    response_data['product_price'][1:].replace(',', '')),
                category=category,
                description=response_data['about_product'][0],
                image=image_file
            )
            product.save()
            products.append(product)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching details for ASIN {i}: {e}")
        except KeyError as e:
            print(f"Error parsing response for ASIN {i}: {e}")

    return products


def download_and_save_image(image_url):
    try:
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(requests.get(image_url).content)
        img_temp.flush()
        return File(img_temp, name=os.path.basename(image_url))
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None
