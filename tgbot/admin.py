from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from dtb.settings import DEBUG

from tgbot.models import Item, Order, RutinUpdate, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "user_id",
        "username",
        "first_name",
        "last_name",
        "address",
        "phone",
        "language_code",
        "deep_link",
        "created_at",
        "updated_at",
        "is_blocked_bot",
    ]
    list_filter = [
        "is_blocked_bot",
    ]
    search_fields = ("username", "user_id")


class ItemInline(admin.TabularInline):
    model = Item
    extra = 1
    fieldsets = (
        (
            ("Item"),
            {
                "fields": (
                    "order",
                    "sales_link",
                    "price_per_unit_in_tl",
                    "count",
                    "size",
                    "color",
                    "detales",
                    "is_available",
                )
            },
        ),
    )

    readonly_fields = (
        "order",
        "sales_link",
        "price_per_unit_in_tl",
        "count",
        "detales",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [ItemInline]
    list_display = (
        "id",
        "user",
        "all_to_pay",
        "is_paid",
        "is_aproved",
        "is_checkedout",
        "is_canceled",
        "is_finished",
    )
    search_fields = ("id", "user", "is_paid")


@admin.register(RutinUpdate)
class RutinUpdateAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "today_price_in_tl",
        "card_no",
        "card_name",
    )
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)
