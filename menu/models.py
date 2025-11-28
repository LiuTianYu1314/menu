from django.core.validators import MaxValueValidator
from django.db import models


class Delicious(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    src = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Psw(models.Model):
    account = models.BigIntegerField(validators=[MaxValueValidator(99999999999)])
    password = models.BigIntegerField(validators=[MaxValueValidator(99999999999)])
    time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.account)  # 返回账号作为字符串表示

class Time(models.Model):
    time = models.DateTimeField(auto_now=True)
    number = models.IntegerField()
    delicious = models.ForeignKey(Delicious, on_delete=models.CASCADE)  # 添加外键关联

    def __str__(self):
        return str(self.time)