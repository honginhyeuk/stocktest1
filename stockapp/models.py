from django.db import models

# Create your models here.
# stockapp/models.py

from django.db import models

class StockData(models.Model):
    ticker = models.CharField(max_length=10)
    date = models.DateField()
    close = models.FloatField()
    rsi = models.FloatField()
    bollinger_high = models.FloatField()
    bollinger_low = models.FloatField()

    def __str__(self):
        return f"{self.ticker} on {self.date}"