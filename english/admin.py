from django.contrib import admin

# 别忘了导入English
from .models import *


# 注册数据模型
admin.site.register(Source)
admin.site.register(Reference)
admin.site.register(Tag)

