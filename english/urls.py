"""jays URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path



from . import views

app_name = 'english'

urlpatterns = [
    # 返回首页
    path('', views.index, name='index'),

    # 来源列表

    # Tag列表
    path('tag_list/<int:id>/', views.tag_list, name='tag_list'),

    # Source列表
    path('source_list/<str:source_type>/', views.source_list, name='source_list'),

    # 英语笔记列表by Source
    path('list_by_source/<int:id>/', views.list_by_source, name='english_list'),

    # 英语笔记列表by Tag
    # get方法
    path('list_by_tag_get/<int:id>/', views.list_by_tag_get, name='list_by_tag'),

    # post方法
    path('list_by_tag_post/', views.list_by_tag_post, name='list_by_tag'),

    # 英语笔记详情
    path('detail/<int:id>/', views.english_detail, name='english_detail'),

    # 英语笔记录入界面
    path('input/<int:id>/', views.input, name='input'),

    # 提交英语笔记
    path('submit/', views.submit, name='submit'),

    # 提交到Word Bench
    path('word_bench/<str:method>/<str:source_type>/', views.word_bench, name='submit'),


    # 提交到Word Bench
    path('list_by_word/<str:id>/', views.list_by_word, name='submit'),

    # 我的总结
    path('summary/', views.summary, name='submit'),




]
