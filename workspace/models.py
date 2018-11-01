from django.db import models
from django.contrib.auth.models import AbstractUser


class MyUser(AbstractUser):
    phone = models.CharField(max_length=11, null=True, unique=True, blank=True, verbose_name="手机号码")
    emailpasswd = models.CharField(max_length=100, verbose_name="邮箱密码")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name


class DailyReports(models.Model):
    date = models.DateField(auto_now_add=True)
    week = models.IntegerField(verbose_name="星期")
    project = models.CharField(max_length=64, verbose_name="项目名称")
    working_time = models.FloatField(verbose_name="工时")
    content = models.TextField(verbose_name="工作内容")
    creator = models.CharField(max_length=32, verbose_name="创建人")

    def __str__(self):
        return str(self.date) + ":" + str(self.project) + "日报"

    class Meta:
        verbose_name = "项目日报"
        verbose_name_plural = verbose_name


class Project(models.Model):
    name = models.CharField(max_length=64, verbose_name="项目名称")
    stage = models.CharField(max_length=32, verbose_name="项目阶段")
    city = models.CharField(max_length=12, verbose_name="城市")
    operator = models.CharField(max_length=32, verbose_name="运维")
    developer = models.CharField(max_length=32, verbose_name="开发")
    sales = models.CharField(max_length=32, verbose_name="销售")
    manager = models.CharField(max_length=32, verbose_name="项目经理")
    business = models.CharField(max_length=32, verbose_name="业务经理")
    agent = models.CharField(max_length=32, verbose_name="代理商")
    license = models.DateField(verbose_name="授权到期时间")
    maintaince = models.DateField(verbose_name="维保到期时间")
    product = models.CharField(max_length=32, verbose_name="产品版本")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "项目名称"
        verbose_name_plural = verbose_name
