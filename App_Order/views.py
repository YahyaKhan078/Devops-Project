from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import Cart, Order, OrderItem
from App_Shop.models import Product


# ------------------------------
# Helper function
# ------------------------------
def get_user_order(user):
    return Order.objects.filter(user=user, ordered=False).first()


# ------------------------------
# Add to Cart
# ------------------------------

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        item=product,
        purchased=False
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.info(request, "Item quantity updated.")
    else:
        messages.success(request, "Item added to cart.")

    # Redirect back to the page they came from
    return redirect(request.META.get('HTTP_REFERER', 'App_Shop:home'))


# ------------------------------
# Cart Sidebar Data (JSON)
# ------------------------------
@login_required
def cart_sidebar_data(request):
    carts = Cart.objects.filter(user=request.user, purchased=False).select_related('item')
    items = []
    subtotal = 0
    for cart in carts:
        item_total = float(cart.get_total())
        subtotal += item_total
        items.append({
            'pk': cart.item.pk,
            'name': cart.item.name,
            'price': float(cart.item.price),
            'quantity': cart.quantity,
            'total': item_total,
            'image': cart.item.mainimage.url if cart.item.mainimage else '',
            'size': getattr(cart.item, 'size', ''),
        })
    return JsonResponse({
        'items': items,
        'count': len(items),
        'subtotal': subtotal,
    })


# ------------------------------
# View Cart
# ------------------------------

@login_required
def cart_view(request):
    carts = Cart.objects.filter(user=request.user, purchased=False)

    if carts.exists():
        return render(request, 'App_Order/cart.html', {'carts': carts})
    else:
        messages.warning(request, "Your cart is empty.")
        return redirect("App_Shop:home")


# ------------------------------
# Remove from Cart
# ------------------------------

@login_required
def remove_from_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)

    cart_item = Cart.objects.filter(
        user=request.user,
        item=product,
        purchased=False
    ).first()

    if cart_item:
        cart_item.delete()
        messages.warning(request, "Item removed from cart.")
    else:
        messages.info(request, "Item not found in cart.")

    return redirect("App_Order:cart")


# ------------------------------
# Increase Quantity
# ------------------------------

@login_required
def increase_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)

    cart_item = Cart.objects.filter(
        user=request.user,
        item=product,
        purchased=False
    ).first()

    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"{product.name} quantity increased.")
    else:
        messages.info(request, "Item not in cart.")

    return redirect("App_Order:cart")


# ------------------------------
# Decrease Quantity
# ------------------------------

@login_required
def decrease_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)

    cart_item = Cart.objects.filter(
        user=request.user,
        item=product,
        purchased=False
    ).first()

    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        messages.info(request, f"{product.name} quantity updated.")
    else:
        messages.info(request, "Item not in cart.")

    return redirect("App_Order:cart")


# ------------------------------
# Checkout (IMPORTANT)
# ------------------------------

@login_required
def purchase(request):
    carts = Cart.objects.filter(user=request.user, purchased=False)

    if not carts.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect("App_Shop:home")

    # create order
    order = Order.objects.create(
        user=request.user,
        ordered=True
    )

    # move cart → order items
    for cart in carts:
        OrderItem.objects.create(
            order=order,
            product=cart.item,
            quantity=cart.quantity,
            price=cart.item.price
        )

        cart.delete()  # clear cart

    messages.success(request, "Purchase successful!")
    return redirect("App_Order:order_history")

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user, ordered=True)

    return render(request, 'order_history.html', {
        'orders': orders
    })