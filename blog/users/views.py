from django.http import HttpResponse, response, HttpResponseRedirect, JsonResponse
from django.shortcuts import render

from .models import User

from django.views import View
from libs.captcha.captcha import captcha
from utils.response_code import RETCODE
#要安装django-redis
from django_redis import get_redis_connection
from libs.yuntongxun.sms import CCP

from django.core import mail  # 设置邮箱发送信息

import hashlib
from random import randint
import logging
logger = logging.getLogger('django')
# Create your views here.

#定义装饰器
def check_login(fn):
    def wrap(request, *args, **kwargs):
        if 'username' not in request.session or 'uid' not in request.session:
            #检查cookie
            c_username = request.COOKIES.get('username')
            c_uid = request.COOKIES.get('uid')
            if not c_uid or not c_username:
                return HttpResponseRedirect('/user/login')
            else:
                #回写session
                request.session['username'] = c_username
                request.session['uid'] = c_uid
        return fn(request, *args, **kwargs)
    return wrap



def RegView(request):
    #注册页面
    if request.method == 'GET':
        # GET 返回登陆界面
        return render(request, 'users/register.html')
    elif request.method == 'POST':
        # POST 处理提交数据
        username = request.POST.get('username')
        password_1 = request.POST.get('password_1')
        password_2 = request.POST.get('password_2')
        verify_code = request.POST.get('verify_code')
        email = request.POST.get('email')
        # 1 两个密码保持一致
        if password_1 != password_2:
            #return render(request, 'user/register.html')
            #TODO Ajax处理
            return HttpResponse('两次输入密码不一致！！！')
        m = hashlib.md5()
        m.update(password_1.encode())   # 必须二进制
        password_m = m.hexdigest()
        #2 当前用户名是否可用
        old_user = User.objects.filter(username=username)
        if old_user:
            return  HttpResponse('用户名已注册')
        old_user_email = User.objects.filter(email=email)
        if old_user_email:
            return HttpResponse('邮箱已绑定')
        # 3 插入数据【明文】【密文处理数据】
        try:
            user = User.objects.create(username=username, password=password_m)
        except Exception as e:
            ##防止高并非问题，有可能报错-重复插入，【唯一索引注意并发写入问题】
            print('--create user error is %s'%(e))
            return HttpResponse('用户名已注册')

        #免登陆一天
        request.session['username'] = username
        request.session['uid'] = user.id
        #TODO 修改session存储时间为1天


        return  HttpResponse('注册成功')

# class RegView(View):
#     def Reg(self, request):
#         # 注册页面
#         if request.method == 'GET':
#             return render(request, 'users/register.html')
#         elif request.method == 'POST':
#             pass

# class ImageCodeView(View):
# # 图片验证码逻辑
#     def get(self, request):
#         '''
#             1.接收前端传递过来的uuid
#             2.判断uuid是否获取到
#             3.通过调用captcha来生成图片验证码（图片二进制和图片内容）
#             4.将图片保存到redis中
#                 uuid作为key, 图片内容作为value, 同时需要设置一个实效
#             5.图片二进制返回前端
#         '''
#         #1.接收前端传递过来的uuid
#         uuid = request.GET.get('uuid')
#         #2.判断uuid是否获取到
#         if uuid is None:
#             return response.HttpResponseBadRequest('没有传递uuid')
#         #3.通过调用captcha来生成图片验证码（图片二进制和图片内容）
#         text, image = captcha.generate_captcha()
#         #4.将图片保存到redis中
#         #    uuid作为key, 图片内容作为value, 同时需要设置一个实效
#         redis_conn = get_redis_connection('default')
#         #key设置为uuid
#         #seconds 过期秒数 300s 5分钟过期时间
#         #value text
#         redis_conn.setex("img:%s"%uuid, 300, image)
#         #5.图片二进制返回前端
#         return HttpResponse(image, content_type="image/jpeg")

#图片验证码逻辑

def Login(request):
    # 登陆页面
    pass

def ChangePWD(request):
    # 修改密码
    pass

def Logout(request):
    # 退出登陆
    # 删删删session,cookie
    resp = HttpResponseRedirect('/users/login')
    if request.COOKIES:
        resp.delete_cookie('username')
        resp.delete_cookie('uid')
    if request.session:
        del request.session['username']
        del request.session['uid']
    return resp
    pass

def GetImageCodeView(request):
    '''
        1.接收前端传递过来的uuid
        2.判断uuid是否获取到
        3.通过调用captcha来生成图片验证码（图片二进制和图片内容）
        4.将图片保存到redis中
            uuid作为key, 图片内容作为value, 同时需要设置一个实效
        5.图片二进制返回前端
    '''
    #1.接收前端传递过来的uuid
    uuid = request.GET.get('uuid')
    #2.判断uuid是否获取到
    if uuid is None:
        return response.HttpResponseBadRequest('没有传递uuid')
    #3.通过调用captcha来生成图片验证码（图片二进制和图片内容）
    text, image = captcha.generate_captcha() # 此处报错，已改正
    #4.将图片保存到redis中
    #    uuid作为key, 图片内容作为value, 同时需要设置一个实效
    redis_conn = get_redis_connection('default')
    #key设置为uuid
    #seconds 过期秒数 300s 5分钟过期时间
    #value text
    redis_conn.setex("img:%s"%uuid, 300, image)
    #5.图片二进制返回前端
    return HttpResponse(image, content_type="image/jpeg")

# def EmailCodeView(request):
#     '''
#         #1.接收参数
#         #2.参数验证
#             #2.1验证参数是否齐全
#             #2.2图片验证码的验证
#                 连接Redis，获取Redis的图片验证码
#                 判断图片验证码是否存在
#                 如果图片验证码未过期，获取之后删除图片验证码
#                 对比图片验证码
#         #3.生成邮箱验证码
#         #4.保存验证码到Redis
#         #5.发送信息
#         #6.返回响应
#     '''
#     # 1.接收参数
#     email = request.POST.get('mobile')
#
#     image_code = request.POST.get('image_code')
#     uuid = request.POST.get('uuid')
#     # 2.参数验证
#     #   2.1验证参数是否齐全
#     if not all([email, image_code, uuid]):
#         return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必要的参数'})
#     #   2.2图片验证码的验证
#     #       连接Redis，获取Redis的图片验证码
#     redis_conn = get_redis_connection('default')
#     redis_image_code = redis_conn.get("img:%s" % uuid)
#     #       判断图片验证码是否存在
#     if redis_image_code is None:
#         return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '图片验证码已过期'})
#     #       如果图片验证码未过期，获取之后删除图片验证码
#     try:
#         redis_conn.delete("img:%s" % uuid)
#     except Exception as e:
#         logger.error(e)
#     #       对比图片验证码,注意大小写问题，redis数据是bytes类型
#     if redis_image_code.decode().lower() != image_code.lower():
#         return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '图片验证码错误'})
#     # 3.生成邮箱验证码
#     email_code = '%06d'%randint(0,999999)
#     #为了方便后期对比，将邮箱验证码记录到日志中
#     logger.info(email_code)
#     # 4.保存验证码到Redis
#     redis_conn.setex('email:%s'%email, 300, email_code)
#     # 5.发送信息
#     mail.send_mail(subject='博客用户注册', message='您的注册验证码是'+email_code, from_email='1345256562@qq.com',
#                    recipient_list=email)
#     # 6.返回响应
#     return JsonResponse({'code': RETCODE.OK, 'msg': '邮件已发送，请注意查收'})

# class SmsCodeView(View):
#     def get(self, request):
#         '''
#             #1.接收参数
#             #2.参数验证
#                 #2.1验证参数是否齐全
#                 #2.2图片验证码的验证
#                     连接Redis，获取Redis的图片验证码
#                     判断图片验证码是否存在
#                     如果图片验证码未过期，获取之后删除图片验证码
#                     对比图片验证码
#             #3.生成邮箱验证码
#             #4.保存验证码到Redis
#             #5.发送信息
#             #6.返回响应
#         '''
#         # 1.接收参数
#         mobile = request.POST.get('mobile')
#         image_code = request.POST.get('image_code')
#         uuid = request.POST.get('uuid')
#         print([mobile, image_code, uuid])
#         # 2.参数验证
#         #   2.1验证参数是否齐全
#         if not all([mobile, image_code, uuid]):
#             return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必要的参数'})
#         #   2.2图片验证码的验证
#         #       连接Redis，获取Redis的图片验证码
#         redis_conn = get_redis_connection('default')
#         redis_image_code = redis_conn.get("img:%s" % uuid)
#         #       判断图片验证码是否存在
#         if redis_image_code is None:
#             return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '图片验证码已过期'})
#         #       如果图片验证码未过期，获取之后删除图片验证码
#         try:
#             redis_conn.delete("img:%s" % uuid)
#         except Exception as e:
#             logger.error(e)
#         #       对比图片验证码,注意大小写问题，redis数据是bytes类型
#         if redis_image_code.decode().lower() != image_code.lower():
#             return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '图片验证码错误'})
#         # 3.生成邮箱验证码
#         sms_code = '%06d'%randint(0,999999)
#         #为了方便后期对比，将邮箱验证码记录到日志中
#         logger.info(sms_code)
#         # 4.保存验证码到Redis
#         redis_conn.setex('email:%s'%mobile, 300, sms_code)
#         # 5.发送信息
#         ccp = CCP()
#         # 注意： 测试的短信模板编号为1
#         ccp.send_template_sms('18310820688', ['1234', 5], 1)
#         CCP().send_template_sms(mobile, [sms_code, 5], 1)
#         # 6.返回响应
#         return JsonResponse({'code': RETCODE.OK, 'msg': '邮件已发送，请注意查收'})

def get1(request):
    '''
        #1.接收参数
        #2.参数验证
            #2.1验证参数是否齐全
            #2.2图片验证码的验证
                连接Redis，获取Redis的图片验证码
                判断图片验证码是否存在
                如果图片验证码未过期，获取之后删除图片验证码
                对比图片验证码
        #3.生成邮箱验证码
        #4.保存验证码到Redis
        #5.发送信息
        #6.返回响应
    '''
    # 1.接收参数
    mobile = request.POST.get('mobile')
    image_code = request.POST.get('image_code')
    uuid = request.POST.get('uuid')
    print([mobile, image_code, uuid])
    # 2.参数验证
    #   2.1验证参数是否齐全
    if not all([mobile, image_code, uuid]):
        return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必要的参数'})
    #   2.2图片验证码的验证
    #       连接Redis，获取Redis的图片验证码
    redis_conn = get_redis_connection('default')
    redis_image_code = redis_conn.get("img:%s" % uuid)
    #       判断图片验证码是否存在
    if redis_image_code is None:
        return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '图片验证码已过期'})
    #       如果图片验证码未过期，获取之后删除图片验证码
    try:
        redis_conn.delete("img:%s" % uuid)
    except Exception as e:
        logger.error(e)
    #       对比图片验证码,注意大小写问题，redis数据是bytes类型
    if redis_image_code.decode().lower() != image_code.lower():
        return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '图片验证码错误'})
    # 3.生成邮箱验证码
    sms_code = '%06d'%randint(0,999999)
    #为了方便后期对比，将邮箱验证码记录到日志中
    logger.info(sms_code)
    # 4.保存验证码到Redis
    redis_conn.setex('email:%s'%mobile, 300, sms_code)
    # 5.发送信息
    ccp = CCP()
    # 注意： 测试的短信模板编号为1
    ccp.send_template_sms('18310820688', ['1234', 5], 1)
    CCP().send_template_sms(mobile, [sms_code, 5], 1)
    # 6.返回响应
    return JsonResponse({'code': RETCODE.OK, 'msg': '邮件已发送，请注意查收'})
