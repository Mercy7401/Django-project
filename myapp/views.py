from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CheckoutForm
from .models import Order, OrderItem, Product


def home(request):
    products = Product.objects.filter(is_active=True)
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__icontains=query)
        )
    if category in dict(Product.CATEGORY_CHOICES):
        products = products.filter(category=category)

    return render(
        request,
        "home.html",
        {
            "products": products,
            "query": query,
            "selected_category": category,
            "categories": Product.CATEGORY_CHOICES,
        },
    )


def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


def _cart_products(request):
    cart = request.session.get("cart", {})
    products = Product.objects.filter(is_active=True, id__in=cart.keys())
    items = []
    subtotal = Decimal("0.00")
    for product in products:
        quantity = cart.get(str(product.id), 0)
        if not isinstance(quantity, int) or quantity < 1:
            continue
        line_total = product.price * quantity
        items.append(
            {
                "product": product,
                "quantity": quantity,
                "line_total": line_total,
                "available_quantity": min(product.stock, 99),
            }
        )
        subtotal += line_total
    return items, subtotal


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    if product.stock < 1:
        messages.error(request, "This item is currently out of stock.")
        return redirect("home")

    try:
        quantity = int(request.POST.get("quantity", "1"))
    except (TypeError, ValueError):
        quantity = 0
    if quantity < 1 or quantity > 99:
        messages.error(request, "Choose a quantity between 1 and 99.")
        return redirect("home")

    cart = request.session.get("cart", {})
    key = str(product.id)
    next_quantity = cart.get(key, 0) + quantity
    if next_quantity > product.stock:
        messages.error(request, f"Only {product.stock} of this item are available.")
        return redirect("home")
    cart[key] = next_quantity
    request.session["cart"] = cart
    messages.success(request, f"{product.name} added to your bag.")
    next_url = request.POST.get("next", "")
    if url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(next_url)
    return redirect("home")


def cart(request):
    items, subtotal = _cart_products(request)
    return render(request, "cart.html", {"items": items, "subtotal": subtotal})


@require_POST
def update_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart_items = request.session.get("cart", {})
    key = str(product.id)
    try:
        quantity = int(request.POST.get("quantity", "0"))
    except (TypeError, ValueError):
        quantity = 0
    if quantity == 0:
        cart_items.pop(key, None)
        messages.success(request, f"{product.name} removed from your bag.")
    elif 1 <= quantity <= min(product.stock, 99):
        cart_items[key] = quantity
        messages.success(request, "Your bag has been updated.")
    else:
        messages.error(request, f"Choose a quantity between 1 and {min(product.stock, 99)}.")
    request.session["cart"] = cart_items
    return redirect("cart")


def checkout(request):
    items, subtotal = _cart_products(request)
    if not items:
        messages.info(request, "Add something lovely to your bag before checking out.")
        return redirect("home")

    form = CheckoutForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            product_ids = [item["product"].id for item in items]
            locked_products = {
                product.id: product
                for product in Product.objects.select_for_update().filter(
                    id__in=product_ids, is_active=True
                )
            }
            if any(
                item["product"].id not in locked_products
                or item["quantity"] > locked_products[item["product"].id].stock
                for item in items
            ):
                form.add_error(None, "An item in your bag is no longer available in that quantity. Please review your bag.")
                return render(
                    request,
                    "checkout.html",
                    {"form": form, "items": items, "subtotal": subtotal},
                )

            order = form.save()
            for item in items:
                product = locked_products[item["product"].id]
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    unit_price=product.price,
                    quantity=item["quantity"],
                )
                product.stock -= item["quantity"]
                product.save(update_fields=["stock"])

        request.session["cart"] = {}
        return redirect("order_success", reference=order.reference)

    return render(
        request, "checkout.html", {"form": form, "items": items, "subtotal": subtotal}
    )


def order_success(request, reference):
    order = get_object_or_404(Order, reference=reference)
    return render(request, "order_success.html", {"order": order})
