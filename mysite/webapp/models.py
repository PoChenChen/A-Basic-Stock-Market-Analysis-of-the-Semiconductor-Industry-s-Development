from django.db import models

class Industry(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Company(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=100, default='None')
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE)
    rank = models.IntegerField(null=True, blank=True)
    year = models.IntegerField()
    country = models.CharField(max_length=50, default='台灣')

    class Meta:
        unique_together = ('symbol', 'year')

    def __str__(self):
        return f"{self.name} ({self.symbol}) - {self.year}"

class StockPrice(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date = models.DateField()
    open = models.FloatField()
    close = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ('company', 'date')