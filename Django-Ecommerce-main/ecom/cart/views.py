from django.shortcuts import render, get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse
from django.contrib import messages


def cart_summary(request):
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()

    quantity_range = range(1, 6)

    context = {
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": totals,
        "quantity_range": quantity_range
    }

    return render(request, "cart_summary.html", context)


def cart_add(request):
    cart = Cart(request)

    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        product = get_object_or_404(Product, id=product_id)
        cart.add(product=product, quantity=product_qty)

        cart_quantity = cart.__len__()

        response = JsonResponse({'qty': cart_quantity})
        messages.success(request, ("Product Added To Cart..."))
        return response


def cart_update(request):
    """Handle cart updates from both product page and cart summary"""
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        product_qty = request.POST.get("product_qty")

        # Convert to integers
        try:
            product_id = int(product_id)
            product_qty = int(product_qty)
        except (ValueError, TypeError):
            return JsonResponse({
                "message": "Invalid data",
                "tag": "error"
            }, status=400)

        cart = Cart(request)

        # Use the update method from Cart class
        cart.update(product=product_id, quantity=product_qty)

        # Return JSON response
        response = {
            "qty": cart.__len__(),
            "total": float(cart.cart_total()),
            "message": "Cart updated!",
            "tag": "success"
        }
        return JsonResponse(response)

    return JsonResponse({
        "message": "Invalid request",
        "tag": "error"
    }, status=400)


def cart_delete(request):
    """Handle cart item deletion"""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')

        cart = Cart(request)
        cart.delete(product=product_id)

        return JsonResponse({
            'success': True,
            'qty': cart.__len__(),
            'total': float(cart.cart_total()),
            'message': 'Item removed from cart!',
            'tag': 'success'
        })

    return JsonResponse({
        'success': False,
        'message': 'Invalid request',
        'tag': 'error'
    }, status=400)