from __future__ import annotations

import uuid
from typing import Optional, Tuple, Union

from django.db import models
from django.db.models import Manager, QuerySet
from django.utils.crypto import get_random_string
from dtb.settings import DEBUG
from telegram import Update
from telegram.ext import CallbackContext
from utils.models import (
    CreateTracker,
    CreateUpdateTracker,
    GetOrNoneManager,
    nb,
)

from tgbot.handlers.utils.info import extract_user_data_from_update


class AdminUserManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_admin=True)


class User(CreateUpdateTracker):
    user_id = models.PositiveBigIntegerField(primary_key=True)  # telegram_id
    username = models.CharField(max_length=32, **nb)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256, **nb)
    address = models.CharField(max_length=256, **nb)
    email = models.CharField(max_length=256, **nb)
    phone = models.CharField(max_length=32, **nb)
    language_code = models.CharField(
        max_length=8, help_text="Telegram client's lang", **nb
    )
    deep_link = models.CharField(max_length=64, **nb)

    is_blocked_bot = models.BooleanField(default=False)

    is_admin = models.BooleanField(default=False)

    objects = GetOrNoneManager()
    admins = AdminUserManager()

    def __str__(self):
        return (
            f"@{self.username}"
            if self.username is not None
            else f"{self.user_id}"
        )

    @classmethod
    def get_user_and_created(
        cls, update: Update, context: CallbackContext
    ) -> Tuple[User, bool]:

        data = extract_user_data_from_update(update)
        u, created = cls.objects.update_or_create(
            user_id=data["user_id"], defaults=data
        )

        if created:
            # Save deep_link to User model
            if (
                context is not None
                and context.args is not None
                and len(context.args) > 0
            ):
                payload = context.args[0]
                if (
                    str(payload).strip() != str(data["user_id"]).strip()
                ):  # you can't invite yourself
                    u.deep_link = payload
                    u.save()

        return u, created

    @classmethod
    def get_user(cls, update: Update, context: CallbackContext) -> User:
        u, _ = cls.get_user_and_created(update, context)
        return u

    @classmethod
    def get_user_by_username_or_user_id(
        cls, username_or_user_id: Union[str, int]
    ) -> Optional[User]:
        """Search user in DB, return User or None if not found"""
        username = str(username_or_user_id).replace("@", "").strip().lower()
        if username.isdigit():  # user_id
            return cls.objects.filter(user_id=int(username)).first()
        return cls.objects.filter(username__iexact=username).first()

    @property
    def invited_users(self) -> QuerySet[User]:
        return User.objects.filter(
            deep_link=str(self.user_id), created_at__gt=self.created_at
        )

    @property
    def tg_str(self) -> str:
        if self.username:
            return f"@{self.username}"
        return (
            f"{self.first_name} {self.last_name}"
            if self.last_name
            else f"{self.first_name}"
        )


# TODO: transaction atomic
class Order(CreateTracker):
    id = models.CharField(
        max_length=8,
        primary_key=True,
        default=get_random_string(8),
        editable=False,
        unique=True,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    all_to_pay = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_aproved = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    is_checkedout = models.BooleanField(default=False)
    is_canceled = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
    # order_tracking = models.AutoField(
    #     default=get_random_string(8), editable=False, unique=True
    # )

    def __str__(self):
        return f"Tracking id: {self.id}\nuser: {self.user}, created at {self.created_at.strftime('(%H:%M, %d %B %Y)')}, All to pay is: {self.all_to_pay}, Payment verification: {self.is_paid}"


# TODO: transaction atomic
class Item(CreateTracker):
    id = models.AutoField(
        primary_key=True,
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    sales_link = models.CharField(max_length=1024, **nb, default="")

    price_per_unit_in_tl = models.DecimalField(
        max_digits=6, decimal_places=2, default=0
    )
    count = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=256, **nb, default="")
    size = models.CharField(max_length=128, **nb, default="")
    detales = models.CharField(max_length=1024, **nb, default="")
    to_pay = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_available = models.BooleanField(default=False)

    def to_pay_in_tl(self):
        return self.price_per_unit_in_tl * self.count


class RutinUpdate(CreateTracker):
    created_at = models.DateTimeField(auto_now_add=True)
    today_price_in_tl = models.DecimalField(
        max_digits=6, decimal_places=2, default=0
    )
    card_no = models.CharField(max_length=32, **nb)
    card_name = models.CharField(max_length=32, **nb)
