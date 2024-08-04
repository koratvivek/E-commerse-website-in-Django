# myapp/admin.py

from .models import Category1
from django.contrib import admin
from .models import Category, Customer, Order, Products, CartItem, Bid
from .utils import send_html_email
from django.template.loader import render_to_string
admin.site.register(Category)
admin.site.register(Customer)
# admin.site.register(Order)
admin.site.register(Products)
admin.site.register(CartItem)
admin.site.register(Bid)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'customer', 'quantity',
                    'price', 'address', 'phone', 'date', 'status')
    actions = ['confirm_orders']
    list_filter = ('status', 'date', 'customer')

    def confirm_orders(self, request, queryset):
        customer_orders = {}

        for order in queryset:
            order.status = True
            order.save()
            cart_item_ids = order.cart_item_ids.split(',')
            CartItem.objects.filter(id__in=cart_item_ids).delete()

            if order.customer.id not in customer_orders:
                customer_orders[order.customer.id] = []

            customer_orders[order.customer.id].append(order)

        for customer_id, orders in customer_orders.items():
            customer = Customer.objects.get(id=customer_id)
            all_confirmed = Order.objects.filter(
                customer=customer, status=False).count() == 0

            if all_confirmed:
                self.send_confirmation_email(customer, orders)

        self.message_user(
            request, "Selected orders have been confirmed and cart items removed.")
    confirm_orders.short_description = 'Confirm selected orders'

    def send_confirmation_email(self, customer, orders):
        subject = 'All Your Orders are Confirmed'

        address = orders[0].address if orders else "No Address"

        message_html = render_to_string('order_confirmation_email.html', {
            'customer': customer,
            'orders': orders,
            'address': address,
        })

        recipient_list = ['your-email@gmail.com']

        send_html_email(subject, message_html, recipient_list)


admin.site.register(Order, OrderAdmin)


class SubcategoryInline(admin.StackedInline):
    model = Category1
    extra = 1
    fk_name = 'parent'


@admin.register(Category1)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent']
    inlines = [SubcategoryInline]
