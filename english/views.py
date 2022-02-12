# 引入redirect重定向模块
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q



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

    # 如果没有音频，则创建音频
    if english_text_detail.audio_name == None:

        # 创建音频
        text = english_text_detail.english_text
        audio_name = str(english_text_detail.id) + '.mp3'
        audio_src = audio_src + audio_name
        tts = gTTS(text)
        tts.save(audio_src)
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
def input(request, id):

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
        print(last_english_text)

        last_reference = last_english_text.reference

        print(last_reference.id)

        ''' 
        列出最新笔记所在页码之后的10页，即 last_reference.id+10
        '''
        # 找出书名
        source = Source.objects.get(id=id)

        # 找出当前有笔记的页码往后10页的范围
        reference_range = reference.filter(id__in = range(last_reference.id,last_reference.id+8))
        print(reference_range)

    # 如果Table English没有记录。
    else:
        ''' 
        列出页码1-5
        '''
        # 找出书名
        source = Source.objects.get(id=id)
        #
        last_english_text = None
        print(last_english_text)

        last_reference = reference.all().first()
        print(last_reference.id)

        reference_range = reference.all()[0:8]
        print(reference_range)

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


    print(tag_dict)
    #####################################################

    context = {
        'tag_dict': tag_dict,
        'all_tag_list': all_tag_list,
        'reference_range': reference_range,
        'source': source,
        'last_reference': last_reference,
        'last_english_text': last_english_text
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
    key_words = request.POST.get('key_words')
    key_expressions = request.POST.get('key_expressions')
    words_to_learn = request.POST.get('words_to_learn')
    note = request.POST.get('note')
    # category = request.POST.get('category')
    reference = request.POST.get('reference')
    created_time = datetime.datetime.now()
    modified_time = datetime.datetime.now()
    author = 10




    # 实例化
    english = English()

    reference_obj = Reference.objects.get(id=reference)
    # category_obj = Category.objects.get(id=category)

    # 准备回到笔记录入的url
    source_id = reference_obj.source_id
    print(source_id)
    global web_url
    input_url = web_url+"english/input/"+str(source_id)+"/"


    #校验数据：笔记正文和笔记标签不能为空！
    if (len(english_text) == 0) | (len(reference) == 0):
        submission_result = "Failed: Required Input Left Empty!"
        time_dalay = 600000
        context = {'submission_result': submission_result, 'all_data': all_data, 'input_url': input_url, 'time_dalay': time_dalay}
        return render(request, 'submit.html', context)



    # 赋值
    english.english_text = english_text
    english.key_words = key_words
    english.key_expressions = key_expressions
    english.words_to_learn = words_to_learn
    english.note = note
    # english.category = category_obj
    english.reference = reference_obj


    english.created_time = created_time
    english.modified_time = modified_time
    #english.author = author

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
    audio_src = audio_src + audio_name
    tts = gTTS(text)
    tts.save(audio_src)
    # 并把名字记入数据库
    english.audio_name = audio_name
    english.save()



    submission_result = "Succeed!"

    if submission_result == "Succeed!":
        time_dalay = 500
        context = {'submission_result': submission_result, 'all_data': all_data, 'input_url': input_url,
                   'time_dalay': time_dalay}
        return render(request, 'submit.html', context)