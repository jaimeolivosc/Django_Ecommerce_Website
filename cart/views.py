from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
import random

from .models import Cart, Order, OrderItem
from .forms import QuantityForm
from ecommerce.models import Product
from user.models import UserProfile
from .forms import ShippingInfoForm


global_random_number = None


@login_required
def add_to_cart(request, product_id):

    if request.method == 'POST':
        '''Add item(s) to the shopping card pressing button from product detail page '''
        product = Product.objects.get(id=product_id)
        cart_item = Cart.objects.filter(user=request.user, product=product).first()

        quantity = request.POST.get('quantity')

        if cart_item:
            #if product already exists
            cart_item.quantity = cart_item.quantity + int(quantity)
            cart_item.save()
            messages.success(request, 'Item added to your cart')

        else:
            #if product still not exists
            cart_item = Cart.objects.create(user=request.user, product=product)
            cart_item.quantity = int(quantity)
            cart_item.save()
            messages.success(request, 'Item added to your cart')

    elif request.method == 'GET':
        '''Add item to the shopping card pressing button from main page (quantity always 1)'''

        product = Product.objects.get(id=product_id)
        cart_item = Cart.objects.filter(user=request.user, product=product).first()

        if cart_item:
            #if product already exists
            cart_item.quantity = cart_item.quantity + 1
            cart_item.save()
            messages.success(request, 'Item added to your cart')

        else:
            #if product still not exists
            Cart.objects.create(user=request.user, product=product)
            messages.success(request, 'Item added to your cart')
        
    referer = request.META.get('HTTP_REFERER')
    
    return HttpResponseRedirect(referer)


def add_to_cart_unknown_user(request):

    messages.success(request, 'To add a product to the shopping cart please sign in.')
    
    referer = request.META.get('HTTP_REFERER')
    
    return HttpResponseRedirect(referer)


@login_required
def cart_details(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.quantity * (item.product.sale_price if item.product.on_sale else item.product.price) for item in cart_items)

    return render(request, "cart/cart_details.html", {"cart_items": cart_items, "total_price": total_price})


@login_required
def update_cart_item(request, cart_item_id):

    cart_item = get_object_or_404(Cart, id=cart_item_id)

    if cart_item.user == request.user:
        if request.method == "POST":    

            new_quantity = request.POST.get('quantity')
            if new_quantity.isdigit() and int(new_quantity) > 0:
                cart_item.quantity = int(new_quantity)
                cart_item.save()
                messages.success(request, "Cart item quantity updated successfully")
            else:
                messages.error(request, "Invalid quantity value")
    
    return redirect('cart:cart_details')


@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id)

    if cart_item.user == request.user:
        cart_item.delete()
        messages.success(request, "Item removed from your cart.")

    return redirect("cart:cart_details")


@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user)
    profile = UserProfile.objects.filter(user=request.user).first()
    total_price = sum(item.quantity * (item.product.sale_price if item.product.on_sale else item.product.price) for item in cart)
    
    global global_random_number
    global_random_number = random.randint(100000, 999999)

    if request.method == 'POST':
        form = ShippingInfoForm(request.POST)
        if form.is_valid():
            phone = request.POST["phone"]
            address = request.POST["address"]
            additional_address = request.POST["additional_address"]
            city = request.POST["city"]
            region = request.POST["region"]
            zip_code = request.POST["zip_code"]
            country = request.POST["country"]
            
            profile.phone = phone
            profile.address = address
            profile.additional_address = additional_address
            profile.city = city
            profile.region = region
            profile.zip_code = zip_code
            profile.country = country

            profile.save()
            messages.success(request, "Shipping information has been updated.")


    if request.method == 'GET':
        form = ShippingInfoForm(instance=profile)
    
    return render(request, 'cart/checkout.html', {'cart': cart, 'form': form, 'total_price': total_price, 'global_random_number': global_random_number})


@login_required
def payment_completed(request, order_id):
    '''Form order and render "Successful page"'''
    
    cart = Cart.objects.filter(user=request.user)
    profile = UserProfile.objects.filter(user=request.user).first()

    total_price = sum(item.quantity * item.product.price for item in cart)

    if cart:
        order = Order.objects.create(order_number=order_id, user=request.user,
                                    ship_info=profile, amount_paid=total_price)
        
        order_items_list = []
        for cart_element in cart:
            order_item = OrderItem.objects.create(order=order, product=cart_element.product,
                                    user=request.user, quantity=cart_element.quantity,
                                    price=cart_element.product.price)
            
            order_items_list.append(order_item)
        
        cart.delete()

    else:
        
        return redirect('/')

    return render(request, 'cart/payment-completed.html', {'order': order, 'order_items_list': order_items_list})


@login_required
def order_details(request, order_num):
    '''View order details'''

    order = Order.objects.filter(user=request.user, order_number=order_num).first()
    order_items = OrderItem.objects.filter(user=request.user, order=order.id)

    return render(request, 'cart/order_details.html', {'order': order, 'order_items': order_items})


@login_required
def list_orders(request):
    '''View order list'''

    orders = Order.objects.filter(user=request.user)

    order_items_list = []
    for order in orders:
        order_items = OrderItem.objects.filter(user=request.user, order=order.id)
        order_items_list.append(order_items)

    return render(request, 'cart/list_orders.html', {'orders': orders, 'order_items_list': order_items_list})


@login_required
def buy_it_now(request, product_id):

    product = Product.objects.get(id=product_id)
    profile = UserProfile.objects.filter(user=request.user).first()

    if product.on_sale:
        total_price = product.sale_price
    else:
        total_price = product.price

    global global_random_number
    global_random_number = random.randint(100000, 999999)
    
    if request.method == 'POST':
        form = ShippingInfoForm(request.POST)
        if form.is_valid():
            phone = request.POST["phone"]
            address = request.POST["address"]
            additional_address = request.POST["additional_address"]
            city = request.POST["city"]
            region = request.POST["region"]
            zip_code = request.POST["zip_code"]
            country = request.POST["country"]
            
            profile.phone = phone
            profile.address = address
            profile.additional_address = additional_address
            profile.city = city
            profile.region = region
            profile.zip_code = zip_code
            profile.country = country

            profile.save()
            messages.success(request, "Shipping information has been updated.")


    if request.method == 'GET':
        form = ShippingInfoForm(instance=profile)

    return render(request, 'cart/buy_it_now.html', {'product': product, 'form': form, 'total_price': total_price, 'global_random_number': global_random_number})