'''
    中间件 5种
        process_request : request -> HttpResponse/None
        process_view : request, callback, callback_args, callback_kwargs -> HttpResponse/None
        process_response : request, response -> HttpResponse
        process_exception : request, exception -> HttpResponse
        process_template_response : request, response ->
'''

from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse

from django.conf import settings    # 需要用到settings中的邮箱配置
from django.core import mail    # 设置邮箱发送报错信息
import traceback  # 追溯报错使用
import re

class ExceptionMW(MiddlewareMixin):
    '''
        需要settings中注册中间件
    '''
    def process_Exception(self, request, exception):
        #异常报错中间件
        print(exception)
        print(traceback.format_exc())
        mail.send_mail(subject='MyNote项目报错溯源', message=traceback.format_exc(), from_email='1345256562@qq.com', recipient_list=settings.EX_MAIL)
        #subject：邮件标题
        #message：普通邮件正文， 普通字符串
        #from_email：发件人
        #recipient_list：收件人列表
        #html_message：多媒体邮件正文，可以是html字符串
        return HttpResponse('网页繁忙，捕获异常中间件（记得修改）')




