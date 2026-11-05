from django.test import TestCase
from django.urls import reverse

from .models import Order, OrderItem, Product


class StorefrontTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Aster Lamp",
            slug="aster-lamp",
            category="Lighting",
            description="A warm light for quiet evenings.",
            price="48.00",
            image_url="https://example.com/lamp.jpg",
            stock=5,
        )

    def test_home_displays_catalog_and_search_filters_products(self):
        response = self.client.get(reverse("home"), {"q": "Aster"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aster Lamp")
        self.assertNotContains(response, "Nothing here just yet.")

        response = self.client.get(reverse("home"), {"q": "not-a-product"})
        self.assertContains(response, "Nothing here just yet.")

    def test_category_filter_and_invalid_category(self):
        response = self.client.get(reverse("home"), {"category": "Lighting"})
        self.assertContains(response, "Aster Lamp")

        response = self.client.get(reverse("home"), {"category": "Unknown"})
        self.assertContains(response, "Aster Lamp")

    def test_adding_product_updates_session_bag(self):
        response = self.client.post(
            reverse("add_to_cart", args=[self.product.id]), {"quantity": 2}
        )

        self.assertRedirects(response, reverse("home"))
        self.assertEqual(self.client.session["cart"], {str(self.product.id): 2})
        self.assertContains(self.client.get(reverse("cart")), "$96.00")

    def test_add_to_cart_rejects_quantity_above_inventory(self):
        self.client.post(
            reverse("add_to_cart", args=[self.product.id]), {"quantity": 6}
        )

        self.assertNotIn("cart", self.client.session)

    def test_adding_product_rejects_external_redirect(self):
        response = self.client.post(
            reverse("add_to_cart", args=[self.product.id]),
            {"quantity": 1, "next": "https://example.com/"},
        )

        self.assertRedirects(response, reverse("home"))

    def test_cart_can_update_and_remove_a_product(self):
        session = self.client.session
        session["cart"] = {str(self.product.id): 1}
        session.save()

        response = self.client.post(
            reverse("update_cart", args=[self.product.id]), {"quantity": 3}
        )
        self.assertRedirects(response, reverse("cart"))
        self.assertEqual(self.client.session["cart"][str(self.product.id)], 3)

        self.client.post(
            reverse("update_cart", args=[self.product.id]), {"quantity": 0}
        )
        self.assertEqual(self.client.session["cart"], {})

    def test_checkout_saves_order_decrements_stock_and_clears_bag(self):
        session = self.client.session
        session["cart"] = {str(self.product.id): 2}
        session.save()

        response = self.client.post(
            reverse("checkout"),
            {
                "customer_name": "Avery Customer",
                "email": "avery@example.com",
                "phone": "555-0100",
                "address": "10 Market Street",
                "city": "Portland",
                "postal_code": "97201",
            },
        )

        order = Order.objects.get()
        self.assertRedirects(
            response, reverse("order_success", args=[order.reference])
        )
        self.assertEqual(order.total, 96)
        self.assertEqual(OrderItem.objects.get(order=order).quantity, 2)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        self.assertEqual(self.client.session["cart"], {})

    def test_checkout_rejects_inventory_that_changed(self):
        session = self.client.session
        session["cart"] = {str(self.product.id): 6}
        session.save()

        response = self.client.post(
            reverse("checkout"),
            {
                "customer_name": "Avery Customer",
                "email": "avery@example.com",
                "phone": "555-0100",
                "address": "10 Market Street",
                "city": "Portland",
                "postal_code": "97201",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "no longer available")
        self.assertFalse(Order.objects.exists())
