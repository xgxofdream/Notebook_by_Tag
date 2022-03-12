# 引入redirect重定向模块
from django.shortcuts import render, redirect, get_object_or_404
# from django.conf import settings
from django.contrib.auth.decorators import login_required


import datetime

import os


from gtts import gTTS



# from corenlp_client import CoreNLP # 导入CoreNLP类 # 用于CoreNLP
# corenlp_dir = "C:/corenlp" # CoreNLP地址 # 用于CoreNLP

import english.models
from .models import *


'''
# 全局变量
'''
web_url = 'http://127.0.0.1:8000/'
audio_src = './media/english/text_to_speech/'



def global_params(request):

    global web_url

    return {
        'web_url': web_url,
    }

'''
# 首页
'''

def index(request):
    greetings = 'Hello'
    now = datetime.datetime.now()
    context = {'greetings': greetings, 'current_date': now}
    return render(request, 'index.html', context)


'''
# 列出Reference
'''
@login_required(login_url=web_url + 'admin')
def reference_list(request, source_id):

    '''
    # 用户验证
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    '''

    # 初始化 context, source_type
    context = {}
    display_page_relevant = ''
    display_page_irrelevant = ''

    source = Source.objects.get(id=source_id)


    if source.type == 'UQ Email':
        display_page_relevant = 'none'
        display_page_irrelevant = ''
    else:
        display_page_relevant = ''
        display_page_irrelevant = 'none'

    reference = Reference.objects.filter(source_id=source_id)



    context.update({
        'reference': reference,
        'source_id':source_id,
        'source': source,
        'display_page_relevant':display_page_relevant,
        'display_page_irrelevant':display_page_irrelevant,
    })

    return render(request, 'reference_list.html', context)




'''
# 列出Source
'''

def source_list(request, source_type):


    # 初始化 context
    context = {}

    # 调用source的类型数据
    source_dict = Source().source_summary()

    # 读取相应的source数据
    source = Source().source_list(source_type)


    context.update({
        'source': source,
        'source_dict': source_dict,
        'source_type': source_type,
    })

    return render(request, 'source_list.html', context)



'''
# 列出Tag
'''
def tag_list(request, id):
    # 调用
    data = Tag().tag_list(id)

    # 返回值
    all_tag_list = data['all_tag_list']
    tag_dict = data['tag_dict']

    context = {'all_tag_list': all_tag_list, 'tag_dict': tag_dict}
    return render(request, 'tag_list.html', context)


'''
# 英语笔记列表by Tag
# Get 方法
'''
def list_by_tag_get(request, id):

    # 实例化Tag
    tag_obj = Tag.objects.get(id=id)
    # 实例化Tag, 但是tag_set当前是QuerySet类型，没有实例（比如tag_obj)的“实例.属性”功能
    tag_set = Tag.objects.filter(id=id)

    # 获取 Table_Eglish中的items;
    # 注意notes in Model_English:tag = models.ManyToManyField(to=Tag, related_name="notes", null=True)
    all_english_text = tag_obj.notes.all()

    # 把笔记中的key_words 和 key_expressions高亮显示出来 via English的功能：text_highlight
    english_styled = {};
    for item in all_english_text:
        single_english_note = item.text_highlight(item)
        english_styled.update(single_english_note)



    # 实例化一个English
    english = English()

    # 读取对tags的统计数据
    data_tag = english.english_to_tag(all_english_text)

    # 读取对sources的统计数据
    data_source = english.english_to_source(all_english_text)


    # 需要传递给模板的对象
    context = {
        'all_english_text': all_english_text,
        'tag_set': tag_set,
        'english_styled': english_styled,
        'statistics_tag': data_tag['statistics_tag'],
        'statistics_source': data_source['statistics_source'],

    }

    return render(request, 'list_by_tag.html', context)


'''
# 英语笔记列表by Tag
# Post 方法
'''
def list_by_tag_post(request):

    # 获取 POST 参数
    all_tag = request.POST.getlist('tag_list')
    intersect_or_not = request.POST.get('intersect')

    # 实例化一个English
    english = English()

    # 读取数据库-Table English
    data_english = english.tag_to_english(all_tag, intersect_or_not)

    # 读取对tags的统计数据
    data_tag = english.english_to_tag(data_english['all_english_text'])

    # 读取对sources的统计数据
    data_source = english.english_to_source(data_english['all_english_text'])

    # 需要传递给模板的对象
    context = {
        'all_english_text': data_english['all_english_text'],
        'intersect_or_not': data_english['intersect_or_not'],
        'tag_set': data_english['tag_set'],
        'english_styled': data_english['english_styled'],
        'statistics_tag': data_tag['statistics_tag'],
        'dict_english_to_tag': data_tag['dict_english_to_tag'],
        'statistics_source': data_source['statistics_source'],
    }

    return render(request, 'list_by_tag.html', context)

'''
# 英语笔记列表by Source
'''
def list_by_source(request, id):

    # 实例化一个English
    english = English()

    # 读取数据库-Table English
    data_english = english.source_to_english(id)

    # 读取对tags的统计数据
    data_tag = english.english_to_tag(data_english['english'])

    # 读取对sources的统计数据
    data_source = english.english_to_source(data_english['english'])


    context = {
        'source': data_english['source'],
        'reference': data_english['reference'],
        'english': data_english['english'],
        'english_styled': data_english['english_styled'],
        'statistics_tag': data_tag['statistics_tag'],
        'dict_english_to_tag': data_tag['dict_english_to_tag'],
        'statistics_source': data_source['statistics_source'],

    }

    return render(request, 'list_by_source.html', context)


'''
# 英语笔记详情
'''
def english_detail(request, id):

    global audio_src

    # 获取对应的English实例 by id
    english_text_detail = get_object_or_404(English, id=id)

    # 把笔记中的key_words 和 key_expressions高亮显示出来 via English的功能：text_highlight
    english_dict = {};
    single_english_note = english_text_detail.text_highlight(english_text_detail)
    english_dict.update(single_english_note)



    # 获取对应的Reference实例
    reference = english_text_detail.reference

    # 获取对应的Reference实例
    source = reference.source

    # 正向查询:获取对应的Tag实例;
    tag = english_text_detail.tag.all()

    # 正向查询:获取Element对应的Tag实例;
    element = Element()
    element2 = Element.objects.filter(english_id=id)
    data = element.element_to_tag(element2)
    statistics_tag = data['statistics_tag']

    # 如果没有音频，则创建音频
    if english_text_detail.audio_name == None:

        # 创建音频
        text = english_text_detail.english_text
        audio_name = str(english_text_detail.id) + '.mp3'
        audio_file_location = audio_src + audio_name
        tts = gTTS(text)
        tts.save(audio_file_location)
        # 并把名字记入数据库
        english_text_detail.audio_name = audio_name
        english_text_detail.save()



    # 需要传递给模板的对象
    context = {
        'english_text_detail': english_text_detail,
        'english_dict': english_dict,
        'reference': reference,
        'tag': tag,
        'source': source,
        'element': element,
        'statistics_tag':statistics_tag,
    }

    # 载入模板，并返回context对象
    return render(request, 'detail.html', context)


'''
# word bench
'''
def word_bench(request, method, source_type):

    # 初始化 context
    context = {}

    '''准备页面的基本数据'''
    # 调用
    data = Tag().tag_list(0)

    # 返回值
    all_tag_list = data['all_tag_list']
    tag_dict = data['tag_dict']

    # source option
    source = Source()
    source_dict = source.source_summary()

    context.update({
        'all_tag_list': all_tag_list,
        'tag_dict': tag_dict,
        'source_dict': source_dict,
    })

    '''只显示Word bench的操作界面'''
    if method == 'None':
        context = context

    '''单词按词性分类（Source来源）'''
    if method == 'source':

        data = English().word_bench(method, source_type)
        context.update(data)

    '''单词按词性分类(Tag来源）'''
    if method == 'tag':
        # 获取 POST 参数
        if request.POST.getlist('tag_list'):
            all_tag = request.POST.getlist('tag_list')
            intersect = request.POST.get('intersect')
            method = request.POST.get('method')

            # 调用tag_to_english,查询出所有符合条件的english notes
            data = English().tag_to_english(all_tag, intersect)
            english_id_list = data['english_id_list']

            # 调用Word Bench
            data = English().word_bench(method, english_id_list)
            context.update(data)

    return render(request, 'word_bench.html', context)


'''
# list by word
'''
def list_by_word(request, id):

    english = English.objects.filter(~Q(id=0))

    word_str = ''
    word_dict_all = {}

    for item in english:
        word_str = word_str + item.key_words + ','

    # print(word_str)

    # 去掉空格（录入key words时，有时候会带上空格）
    word_str = word_str.replace(' ', '')

    # 转化为list via 逗号
    word_list = word_str.split(',')

    # 去掉list中的空值（因为有的笔记里面，我没有输入key words）
    while '' in word_list:
        word_list.remove('')

    # 去掉重复的元素
    word_list = list(set(word_list))

    # 将list转化成字典，keywords为键，值为空。！！！重复的keyword只会被转化为一个键值(字典的功能）！！！
    for item in word_list:
        word_dict_all.update({item: []})

    # 比对key words，将对应的id装入字典的值中。
    for key in word_dict_all:
        for item in english:
            # 清洗 Table English 里的key_words字段。
            # 载入 key_words, 一个item的key_words可能保存了多个keywords，所以要把他们组成字符串（item_word_str)
            item_word_str = item.key_words
            # 去掉空格（录入key words时，有时候会带上空格）
            item_word_str = item_word_str.replace(' ', '')
            # 转化为list via 逗号
            item_word_list = item_word_str.split(',')



            if key in item_word_list:
                word_dict_all[key].append(item.id)


    # print(word_dict_all)

    # 整部字典
    if id == 'all':
        word_dict = word_dict_all

    else:
        # 对字典切片
        word_dict = {key:value for (key, value) in word_dict_all.items() if key == id }

    context = {'english': english, 'word_dict': word_dict}
    return render(request, 'list_by_word.html', context)

    print(word_dict)


'''
# 我的总结
'''
def summary(request):
    summary = 'be building'
    # 需要传递给模板的对象
    context = {
        'summary': summary,
    }

    # 载入模板，并返回context对象
    return render(request, 'summary.html', context)


'''
# 录入英语笔记
'''
@login_required(login_url=web_url + 'admin')
def input(request, id):
    '''
    # 用户验证
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    '''

    ############# 上一次记录到哪里 (the last English_text_location)#######################
    # 在Referecen表中查询source_id=id的所有记录（即，这本书的所有页码）
    reference = Reference.objects.filter(source_id=id)

    '''
    找到所有英语笔记-->找到最后一条笔记
    '''
    # 在English表中查询能匹配这个reference的所有记录（即，reference_id__in=reference）。它的意思就是在这本书所以页码名下的所有英语笔记。
    all_english_text = English.objects.filter(reference_id__in=reference)

    # 如果Table English 有记录。
    if all_english_text:

        # 找出最后一条记录（即，最后一条英语笔记）
        last_english_text = all_english_text.order_by('id').last()
        english_styled = last_english_text.text_highlight(last_english_text)

        last_reference = last_english_text.reference


        '''
        列出最新笔记所在页码之后的10页，即 last_reference.id+10
        '''
        # 找出书名
        source = Source.objects.get(id=id)

        # 找出当前有笔记的页码往后10页的范围 # 有问题：当不是连续输入的referncence
        reference_range = reference.order_by('id').filter(id__gte=last_reference.id)[:10]
        #print(reference_range)

    # 如果Table English没有记录。
    else:
        '''
        列出页码1-5
        '''
        # 找出书名
        source = Source.objects.get(id=id)
        #
        last_english_text = None
        #print(last_english_text)

        last_reference = reference.all().first()
        #print(last_reference.id)

        reference_range = reference.order_by('id').all()[:10]
        #print(reference_range)

    #####################################################
    ############# listing Tags #######################
    # ~Q(Tag_id=0)： 所有不等于0的items
    all_tag_list = Tag.objects.filter(~Q(id=0))

    # 初始化一个字典
    tag_dict = {}
    # 将数据表转化成字典。注意，item.root重复的键只会保留一个。所以，要对字典的键的值补救。
    for item in all_tag_list:
        # list([item.sub01]):将item.sub01转化为完整不分割的列表
        tag_dict.update({item.root:list([item.sub01])})


    for every_key in tag_dict:
        for item in all_tag_list:
            if every_key == item.root:
                tag_dict[every_key].append(item.sub01)
        # 字典的值去重
        tag_dict[every_key] = list(set(tag_dict[every_key]))



    #####################################################

    context = {
        'tag_dict': tag_dict,
        'all_tag_list': all_tag_list,
        'reference_range': reference_range,
        'source': source,
        'last_reference': last_reference,
        'last_english_text': last_english_text,
        'english_styled':english_styled,
    }
    return render(request, 'input.html', context)


'''
# 提交笔记
'''
def submit(request):
    global audio_src
    # 获取 POST 参数
    all_data = request.body
    english_text = request.POST.get('english_text')

    note = request.POST.get('note')
    # category = request.POST.get('category')
    reference = request.POST.get('reference')
    created_time = datetime.datetime.now()
    modified_time = datetime.datetime.now()
    author = 10

    ##############读取各个Tag下的不笔记数据，并整理成字典########################
    # 调用Tag数据，用于比对input.html中的name和tag.id
    all_tag = Tag().tag_list(0)
    all_tag_list = all_tag['all_tag_list']
    note_dict = {}


    # 将笔记按照tag.id整理成字典
    for item in all_tag_list:

        key_words = []
        key_expressions = []


        data = request.POST.get(str(item.id))
        note_list = data.split(',')

        # 去掉列表note_list中每一个元素的首尾空格
        for i, val in enumerate(note_list):
            note_list[i] = val.strip(' ')


        # 将句子和单词分开整理
        for note_item in note_list:
            if ' ' in note_item:
                key_expressions.append(note_item)
            else:
                key_words.append(note_item)

        # 去掉list中的空值
        while '' in key_expressions:
            key_expressions.remove('')
        while '' in key_words:
            key_words.remove('')

        # 往笔记中分开存储单词和句子
        note_dict[item.id] = {'key_words': key_words, 'key_expressions': key_expressions}

    # print(note_dict)

    ######################################


    # 实例化
    english = English()

    reference_obj = Reference.objects.get(id=reference)
    # category_obj = Category.objects.get(id=category)

    # 准备回到笔记录入的url
    source_id = reference_obj.source_id
    # print(source_id)
    global web_url
    input_url = web_url+"english/input/"+str(source_id)+"/"


    #校验数据：笔记正文和笔记标签不能为空！
    if (len(english_text) == 0) | (len(reference) == 0):
        submission_result = "Failed: Required Input Left Empty!"
        time_dalay = 600000
        context = {'submission_result': submission_result, 'all_data': all_data, 'input_url': input_url, 'time_dalay': time_dalay}
        return render(request, 'submit.html', context)



    # 赋值
    key_words = []
    key_expressions = []

    for key, value in note_dict.items():
        key_words.extend(value['key_words'])
        key_expressions.extend(value['key_expressions'])

    # 去掉list中的空值
    while '' in key_expressions:
        key_expressions.remove('')
    while '' in key_words:
        key_words.remove('')

    key_words = ",".join(key_words)
    key_expressions = ",".join(key_expressions)

    # print(key_words)
    # print(key_expressions)

    english.key_words = key_words
    english.key_expressions = key_expressions
    english.english_text = english_text

    english.note = note
    # english.category = category_obj
    english.reference = reference_obj


   # english.created_time = created_time
   # english.modified_time = modified_time
   # english.author = author

    # 写入数据库
    english.save()

    '''
    # 把English和tag关系写入数据库
    # 只有一个Tag的时候
    tag_obj = Tag.objects.get(id=tag)
    english.tag.add(tag_obj)
    '''
    all_tag = request.POST.getlist('tag_list')


    if all_tag:
        for index in range(len(all_tag)):
            tag_obj = Tag.objects.get(id=all_tag[index])
            english.tag.add(tag_obj)
    else:
        tag_obj = Tag.objects.get(id=1) # id=1是“Not assigned”
        english.tag.add(tag_obj)

    '''
    # 创建音频文件，并把名字记入数据库
    '''
    english = English.objects.all().last()
    # 创建音频
    text = english_text
    audio_name = str(english.id) + '.mp3'
    audio_file_location = audio_src + audio_name
    tts = gTTS(text)
    tts.save(audio_file_location)
    # 并把名字记入数据库
    english.audio_name = audio_name
    english.save()


    '''
     # 从English中读出刚刚写入的笔记，提取keywords，key_expressions录入Element
     '''

    for key, value in note_dict.items():

        tag_obj = Tag.objects.get(id=key)


        key_word_list = value['key_words']
        key_expression_list = value['key_expressions']

        for item in key_word_list:
            element = Element()
            element.english_id = english.id
            element.type = 'key_words'
            element.text = item
            element.save()
            element.tag.add(tag_obj)

        for item in key_expression_list:
            element = Element()
            element.english_id = english.id
            element.type = 'key_expressions'
            element.text = item
            element.save()
            element.tag.add(tag_obj)

    submission_result = "Succeed!"

    if submission_result == "Succeed!":
        time_dalay = 500
        context = {'submission_result': submission_result, 'all_data': all_data, 'input_url': input_url,
                   'time_dalay': time_dalay}
        return render(request, 'submit.html', context)


'''
# 录入Reference
'''
def submit_reference(request):

    all_data = request.body
    source_id = request.POST.get('source_id')

    # 邮件一类的资料集合
    reference_title = request.POST.get('reference_title')
    reference_note = request.POST.get('reference_note')

    # 书本
    start_page = request.POST.get('start_page')
    end_page = request.POST.get('end_page')
    print(start_page)

    if type(reference_title)==type('string'):

        reference = Reference()

        reference.english_text_location = reference_title
        reference.note = reference_note
        reference.source_id = source_id

        # 写入数据库
        reference.save()


    if type(start_page)==type('string') and type(end_page)==type('string'):

        start_page = int(start_page)
        end_page = int(end_page)

        while start_page <= end_page:
            page = 'Page '+str(start_page)
            start_page = start_page + 1

            # 实例化
            reference = Reference()

            # 获取页码
            reference.english_text_location = page
            reference.source_id = source_id

            #print(page)

            # 写入数据库
            reference.save()

            print(reference.save())

    # 回到原页面
    input_url = web_url + "english/reference_list/" + str(source_id) + "/"
    submission_result = "Succeed!"
    time_dalay = 1500
    context = {'submission_result': submission_result, 'input_url': input_url,
               'time_dalay': time_dalay}
    return render(request, 'submit.html', context)


def element_review(request, id):
    # 调用
    data = Tag().tag_list(id)

    # 返回值
    all_tag_list = data['all_tag_list']
    tag_dict = data['tag_dict']

    context = {'all_tag_list': all_tag_list, 'tag_dict': tag_dict}
    return render(request, 'tag_list_for_element.html', context)


'''
# 英语笔记列表by Tag
# Post 方法
'''
def list_for_element(request):

    # 获取 POST 参数
    all_tag = request.POST.getlist('tag_list')
    intersect_or_not = request.POST.get('intersect')

    # 实例化一个Element
    element = Element()

    # 读取数据库-Table Element
    data_element = element.tag_to_element(all_tag, intersect_or_not)

    # 读取数据库-Table English
    element_id_list = data_element['element_id_list']
    data_english = element.element_to_english(element_id_list)




    # 需要传递给模板的对象
    context = {
        'all_element_text': data_element['all_element_text'],
        'intersect_or_not': data_element['intersect_or_not'],
        'tag_set': data_element['tag_set'],
        'english_styled':data_english['english_styled'],


    }

    return render(request, 'list_for_element.html', context)






'''
# 英语笔记列表by Tag
# Post 方法
'''
@login_required(login_url=web_url + 'admin')
def update(request, english_id):

    '''
    # 用户验证
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    '''

    '''
    调取笔记
    '''

    # 获取对应的English实例 by id
    english = get_object_or_404(English, id=english_id)

    # 把笔记中的key_words 和 key_expressions高亮显示出来 via English的功能：text_highlight
    english_dict = {};
    single_english_note = english.text_highlight(english)
    english_dict.update(single_english_note)

    # 获取对应的Reference实例
    reference_current = english.reference

    # 获取对应的source实例
    source = reference_current.source

    # 正向查询:获取对应的Tag实例;
    tag = english.tag.all()

    # 正向查询:获取Element对应的Tag实例;
    element = Element()
    element2 = Element.objects.filter(english_id=english_id)
    data = element.element_to_tag(element2)
    statistics_tag = data['statistics_tag']


    '''
    更新笔记
    '''


    # 在Referecen表中查询source_id=source.id的所有记录（即，这本书的所有页码）
    reference = Reference.objects.filter(source_id=source.id)

    # 找出当前笔记的页码前后5页的范围
    reference_range = reference.order_by('id').filter(id__gte=(reference_current.id-5))[:10]


    #####################################################
    ############# listing Tags #######################
    # ~Q(Tag_id=0)： 所有不等于0的items
    all_tag_list = Tag.objects.filter(~Q(id=0))

    # 初始化一个字典
    tag_dict = {}
    # 将数据表转化成字典。注意，item.root重复的键只会保留一个。所以，要对字典的键的值补救。
    for item in all_tag_list:
        # list([item.sub01]):将item.sub01转化为完整不分割的列表
        tag_dict.update({item.root:list([item.sub01])})


    for every_key in tag_dict:
        for item in all_tag_list:
            if every_key == item.root:
                tag_dict[every_key].append(item.sub01)
        # 字典的值去重
        tag_dict[every_key] = list(set(tag_dict[every_key]))




    # 需要传递给模板的对象
    context = {
        'english': english,
        'english_dict': english_dict,
        'reference_current':reference_current,

        'reference': reference,
        'tag': tag,
        'source': source,
        'element': element,
        'statistics_tag':statistics_tag,

        'tag_dict': tag_dict,
        'all_tag_list': all_tag_list,
        'reference_range': reference_range,

        'element2':element2,

    }

    # 载入模板，并返回context对象
    return render(request, 'update.html', context)


'''
# 提交更新的数据
'''
def submit_update(request, english_id):

    global audio_src

    # 准备url：回到update页面
    global web_url
    input_url = web_url + "english/update/" + str(english_id) + "/"

    # 获取 POST 参数
    all_data = request.body
    english_text = request.POST.get('english_text')
    note = request.POST.get('note')
    reference = request.POST.get('reference')

    '''
    获取前台传来的每个Tag类别下的数据
    '''

    # 调用Tag数据，用于比对input.html中的name和tag.id
    all_tag = Tag().tag_list(0)
    all_tag_list = all_tag['all_tag_list']
    note_dict = {}

    # 将笔记按照tag.id整理成字典
    for item in all_tag_list:

        key_words = []
        key_expressions = []

        # 获取 POST 参数中各个Tag名下的值。item.id是Tag.id,也作为前台Tag的POST参数名
        data = request.POST.get(str(item.id))
        note_list = data.split(',')

        # 去掉列表note_list中每一个元素的首尾空格
        for i, val in enumerate(note_list):
            note_list[i] = val.strip(' ')

        # 将句子和单词分开整理
        for note_item in note_list:
            if ' ' in note_item:
                key_expressions.append(note_item)
            else:
                key_words.append(note_item)

        # 去掉list中的空值
        while '' in key_expressions:
            key_expressions.remove('')
        while '' in key_words:
            key_words.remove('')

        # 往Tag字典中存储单词和句子。item.id就是键值，也即Tag.id
        note_dict[item.id] = {'key_words': key_words, 'key_expressions': key_expressions}


    '''
    将每个Tag类别下的数据整理成字符串，预备存进数据库
    '''
    # 赋值
    key_words = []
    key_expressions = []

    for key, value in note_dict.items():
        key_words.extend(value['key_words'])
        key_expressions.extend(value['key_expressions'])

    # 去掉list中的空值
    while '' in key_expressions:
        key_expressions.remove('')
    while '' in key_words:
        key_words.remove('')

    key_words = ",".join(key_words)
    key_expressions = ",".join(key_expressions)


    '''
    更新数据库
    '''
    # 实例化English
    english = get_object_or_404(English, id=english_id)

    # 将reference存进数据库
    # 获取reference
    reference_obj = Reference.objects.get(id=reference)
    english.reference = reference_obj


    # 将key_words存入数据库
    if key_words:
        english.key_words = key_words

    # 将key_expressions存入数据库
    if key_expressions:
        english.key_expressions = key_expressions

    # 将english_text存入数据库
    if english_text:
        english.english_text = english_text

    # 将note存入数据库
    english.note = note

    # 将modified_time存入数据库
    modified_time = datetime.datetime.now()
    english.modified_time = modified_time

    ################
    ### 更新数据库 ###
    ################
    english.save()

    '''
    把English和tag关系写入数据库
    只有一个Tag的时候：tag_obj = Tag.objects.get(id=tag)，english.tag.add(tag_obj)
    '''
    # 清空之前的tag_english关系
    english.tag.clear()

    # 获取新的tag_english关系
    all_tag = request.POST.getlist('tag_list')

    if all_tag:
        for index in range(len(all_tag)):
            tag_obj = Tag.objects.get(id=all_tag[index])
            english.tag.add(tag_obj)
    # 如果没有任何指定，则默认为Not assigned
    else:
        tag_obj = Tag.objects.get(id=1)  # id=1是“Not assigned”
        english.tag.add(tag_obj)

    '''
    # 更新音频文件，并把名字记入数据库
    '''

    # 获取文本
    text = english_text

    # 创建文件名和路径
    audio_name = str(english.id) + '.mp3'
    audio_file_location = audio_src + audio_name

    # 并把名字记入数据库
    english.audio_name = audio_name
    english.save()

    # 生成语音文件并存储
    tts = gTTS(text)
    tts.save(audio_file_location)


    '''
     # 从English中读出刚刚写入的笔记，提取keywords，key_expressions录入Element
    '''

    # 清空之前的english_element关系
    element = Element()
    element_set = element.english_to_element(english)

    for item in element_set:
        item.tag.clear()
        item.delete()

    # 清空之前的tag_element关系


    for key, value in note_dict.items():

        tag_obj = Tag.objects.get(id=key)

        key_word_list = value['key_words']
        key_expression_list = value['key_expressions']

        for item in key_word_list:
            element = Element()
            element.english_id = english.id
            element.type = 'key_words'
            element.text = item
            element.save()
            element.tag.add(tag_obj)

        for item in key_expression_list:
            element = Element()
            element.english_id = english.id
            element.type = 'key_expressions'
            element.text = item
            element.save()
            element.tag.add(tag_obj)


    '''
    返回更新数据库的结果
    '''
    submission_result = "Succeed!"

    if submission_result == "Succeed!":
        time_dalay = 500
        context = {'submission_result': submission_result, 'all_data': all_data, 'input_url': input_url,
                   'time_dalay': time_dalay}
        return render(request, 'submit.html', context)

