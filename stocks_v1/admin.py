from django.contrib import admin
from stocks_v1.models import Stock, StockTracker, PriceNotification
from simple_history.admin import SimpleHistoryAdmin


class StockHistoryAdmin(SimpleHistoryAdmin):
    history_list_display = ['price', 'prev_price',
                            'open_price', 'percentage_change', 'max_price', 'min_price']


admin.site.register(Stock, StockHistoryAdmin)
admin.site.register(StockTracker)
admin.site.register(PriceNotification)
