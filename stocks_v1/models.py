from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save
from simple_history.models import HistoricalRecords
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Stock(models.Model):
    category = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=20, null=True, blank=True, unique=True)
    ticker = models.CharField(max_length=10, unique=True)
    volume = models.PositiveIntegerField(default=0.00)
    price = models.DecimalField(max_digits=10, default=0, decimal_places=2)
    prev_price = models.DecimalField(
        max_digits=10, default=0, decimal_places=2)
    open_price = models.DecimalField(
        max_digits=10, default=0, decimal_places=2)
    percentage_change = models.DecimalField(
        max_digits=10, default=0, decimal_places=2)
    max_price = models.DecimalField(max_digits=10, default=0, decimal_places=2)
    min_price = models.DecimalField(
        max_digits=10, default=0, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords(related_name='logs')

    @classmethod
    def get_stock(cls, id):
        stock = cls.objects.get(id=id)
        return stock

    @classmethod
    def get_history(cls, ticker, start_date=None, end_date=None):
        if start_date and end_date:
            return cls.history.filter(ticker=ticker, updated_at__date__gte=start_date, updated_at__date__lte=end_date)
        return cls.history.filter(ticker=ticker, updated_at__date=start_date)

    class Meta:
        ordering = ['updated_at']

    def __str__(self):
        return self.ticker


class StockTracker(models.Model):
    investors = models.ManyToManyField(
        User, related_name="trackers")
    stock = models.ForeignKey(Stock, related_name='asset',
                              on_delete=models.CASCADE)
    quote_price = models.DecimalField(max_digits=10, decimal_places=2)
    at_tracking = models.DecimalField(
        max_digits=10, decimal_places=2, null=True)
    matched = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now=True)
    last_updated = models.DateTimeField(auto_now_add=True)
    matched_date = models.DateTimeField(null=True, blank=True)

    def save_tracker(self):
        self.save()
        return self

    def delete_tracker(self):
        self.delete()

    @classmethod
    def get_stock(cls, id):
        stock = cls.objects.get(id=id)
        return stock

    def update_matched(self):
        self.matched_date = timezone.now()
        self.matched = True
        self.save()
        return self

    @classmethod
    def check_match(cls, ticker, quote_price):
        stock = cls.objects.filter(
            stock__ticker=ticker, quote_price=quote_price).first()
        return stock

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return f"{self.stock.ticker}: {self.quote_price}"


class PriceNotification(models.Model):
    subscriber = models.ForeignKey(
        StockTracker, related_name="subscribers", on_delete=models.SET_NULL, null=True)
    viewers = models.ManyToManyField(
        User, related_name="viewed")
    content = models.CharField(max_length=255)
    viewed = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    viewed_date = models.DateTimeField(blank=True, null=True)

    def save_notification(self):
        self.save()
        return self

    def delete_notification(self):
        self.delete()

    @classmethod
    def get_viewed(cls):
        viewed = cls.objects.filter(viewed=True)
        return viewed

    @classmethod
    def get_unviewed(cls):
        unviewed = cls.objects.filter(viewed=False)
        return unviewed

    def __str__(self) -> str:
        return self.content


@receiver(pre_save, sender=StockTracker)
def set_at_tracking(sender, instance, **kwargs):
    instance.at_tracking = instance.stock.price
