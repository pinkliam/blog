from django.db import models

# Create your models here.

# Create your models here.
class User(models.Model):
    #用户名
    username = models.CharField('用户名', max_length=50, unique=True, blank=False)
    #密码
    password = models.CharField('密码', max_length=32, blank=False)
    # 头像信息
    avatar = models.ImageField(upload_to="avatar/%Y%m%d/", blank=True)
    # 简介信息
    user_desc = models.CharField('简介信息', max_length=50, blank=True)
    #邮箱
    email = models.EmailField('邮箱', unique=True,blank=False)
    #注册时间
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    #更新时间
    updated_time = models.DateTimeField('更新时间', auto_now=True)
    #是否活跃
    is_active = models.BooleanField("是否活跃", default=True)

    class Meta:
        db_table = 'users' #修改表名
        verbose_name = 'yonghuguanli' #admin后台显示
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.email
