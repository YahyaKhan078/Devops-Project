from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from decimal import Decimal

# Models
from App_Order.models import Order, OrderItem, Cart
from App_Payment.models import BillingAddress
from App_Payment.forms import BillingForm


# ------------------------------
# Helper
# ------------------------------
def get_active_order(user):
    return Order.objects.filter(user=user, ordered=False).first()


# ------------------------------
# Checkout (address + summary)
# ------------------------------
@login_required
def checkout(request):
    saved_address, _ = BillingAddress.objects.get_or_create(user=request.user)

    form = BillingForm(instance=saved_address)

    if request.method == 'POST':
        form = BillingForm(request.POST, instance=saved_address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shipping address saved!')
            return redirect('App_Payment:checkout')

    carts = Cart.objects.filter(user=request.user, purchased=False)

    if not carts.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('App_Shop:home')

    # calculate total
    total = sum([item.item.price * item.quantity for item in carts])

    return render(request, 'App_Payment/checkout.html', {
        'form': form,
        'carts': carts,
        'order_total': total,
        'saved_address': saved_address
    })


# ------------------------------
# Payment (confirm & place order)
# ------------------------------
@login_required
def payment(request):
    saved_address = BillingAddress.objects.filter(user=request.user).first()

    if not saved_address or not saved_address.is_fully_filled():
        messages.info(request, 'Please complete your shipping address first.')
        return redirect('App_Payment:checkout')

    carts = Cart.objects.filter(user=request.user, purchased=False)

    if not carts.exists():
        messages.warning(request, "Cart is empty.")
        return redirect('App_Shop:home')

    total = sum([item.item.price * item.quantity for item in carts])

    if request.method == 'POST':
        # Create order
        order = Order.objects.create(
            user=request.user,
            ordered=True,
            paymentId='COD',
            orderId=f'ORD-{request.user.pk}-{Order.objects.filter(user=request.user).count() + 1}'
        )

        # Convert cart → order items
        for cart in carts:
            OrderItem.objects.create(
                order=order,
                product=cart.item,
                quantity=cart.quantity,
                price=cart.item.price
            )
            cart.delete()

        messages.success(request, "Order placed successfully!")
        return redirect('App_Order:order_history')

    return render(request, 'App_Payment/payment.html', {
        'carts': carts,
        'order_total': total,
        'saved_address': saved_address,
    })


# ------------------------------
# Payment Complete Callback
# ------------------------------
@csrf_exempt
def complete(request):
    if request.method == 'POST' or request.method == 'GET':
        return render(request, 'App_Payment/complete.html')

    return render(request, 'App_Payment/complete.html')


# ------------------------------
# Finalize Order (legacy SSLCommerz callback — kept for URL compatibility)
# ------------------------------
@login_required
def purchased(request, val_id, tran_id):
    carts = Cart.objects.filter(user=request.user, purchased=False)

    if not carts.exists():
        messages.warning(request, "No items to process.")
        return redirect('App_Shop:home')

    # create order
    order = Order.objects.create(
        user=request.user,
        ordered=True,
        paymentId=val_id,
        orderId=tran_id
    )

    # convert cart → order items
    for cart in carts:
        OrderItem.objects.create(
            order=order,
            product=cart.item,
            quantity=cart.quantity,
            price=cart.item.price
        )
        cart.delete()

    messages.success(request, "Order placed successfully!")
    return redirect('App_Shop:home')


# ------------------------------
# Order History
# ------------------------------
@login_required
def order_view(request):
    orders = Order.objects.filter(user=request.user, ordered=True)

    if not orders.exists():
        messages.info(request, "No orders found.")

    return render(request, 'App_Payment/order.html', {'orders': orders})