from django.urls import path

from . import views


urlpatterns = [
    path('register', views.RegView),
    # path('register', views.RegView.as_view()),

    #图片验证码路由
    path("ImageCode", views.GetImageCodeView),
    # path("ImageCode", views.ImageCodeView.as_view()),

    #短信发送
    # path('smscode', views.SmsCodeView.as_view(), name='smscode')
    path('smscode', views.get1)
]