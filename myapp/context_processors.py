def cart_count(request):
    cart = request.session.get("cart", {})
    return {
        "cart_count": sum(
            quantity
            for quantity in cart.values()
            if isinstance(quantity, int) and quantity > 0
        )
    }
