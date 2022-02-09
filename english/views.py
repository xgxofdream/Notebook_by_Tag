# 引入redirect重定向模块
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q



import datetime

import os


from gtts import gTTS

from stanfordcorenlp import StanfordCoreNLP

# from corenlp_client import CoreNLP # 导入CoreNLP类 # 用于CoreNLP
# corenlp_dir = "C:/corenlp" # CoreNLP地址 # 用于CoreNLP

import english.models
from .models import *


'''
# 全局变量
'''
def global_params(request):
    web_url = 'http://127.0.0.1:8000/'

    return {
        'web_url':web_url,
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
def source_list(request, id):

    source = Source.objects.filter(~Q(id=0))
    if id == 0:
        source = source
        source_type = "All"
    if id == 1:
        source = source.filter(type='Novels')
        source_type = "Novels"
    if id == 2:
        source = source.filter(type='Poems')
        source_type = "Poems"
    if id == 3:
        source = source.filter(type='Reference books')
        source_type = "Reference books"
    if id == 4:
        source = source.filter(type='Autobiography')
        source_type = "Autobiography"
    if id == 5:
        source = source.filter(type='Diary')
        source_type = "Diary"
    if id == 6:
        source = source.filter(type='Textbook')
        source_type = "Textbook"
    if id == 7:
        source = source.filter(type='Elon Mush')
        source_type = "Elon Mush"
    if id == 8:
        source = source.filter(type='王德中Cyrus')
        source_type = "王德中Cyrus"


    context = {'source': source, 'source_type': source_type}
    return render(request, 'source_list.html', context)

'''
# 列出Tag
'''
def tag_list(request):

    # ~Q(source_id=0)： 所有不等于0的items
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
    all_english_text = tag_obj.notes.all().values('english_text', 'id')

    # 需要传递给模板的对象
    context = {'all_english_text': all_english_text, 'tag_set': tag_set}
    return render(request, 'list_by_tag.html', context)



'''
# 英语笔记列表by Tag
# Post 方法
'''
def list_by_tag_post(request):

    # 获取 POST 参数
    all_tag = request.POST.getlist('tag_list')
    intersect = request.POST.get('intersect')

    # 实例化Tag
    tag_set = Tag.objects.filter(id__in=all_tag)

    arr_query = list(all_tag)


    for index in range(len(all_tag)):
        tag_obj = Tag.objects.get(id=all_tag[index])

        all_english_text = tag_obj.notes.all().values('english_text', 'id')

        arr_query[index] = all_english_text

    ''''''
    # Tag的交集/并集运算
    if intersect == 'no':
        for index in range(len(arr_query)):
            all_english_text = all_english_text | arr_query[index]

    if intersect == 'yes':
        for index in range(len(arr_query)):
            all_english_text = all_english_text & arr_query[index]

    # 去除重复items
    all_english_text = all_english_text.order_by('id').distinct()


    # 需要传递给模板的对象
    context = {'all_english_text': all_english_text, 'intersect_or_not': intersect, 'tag_set': tag_set}
    return render(request, 'list_by_tag.html', context)

'''
# 英语笔记列表by Source
'''
def list_by_source(request, id):

    source = Source.objects.get(id=id)

    # Reference的__str__一定要放回str类型的数据，不然报错！很奇怪！
    reference = Reference.objects.filter(source_id=id)
    reference_id = reference.values('id')

    english = English.objects.filter(reference_id__in=reference_id)

    context = {
        'reference': reference,
        'english': english,
        'source': source,
    }

    return render(request, 'list_by_source.html', context)



'''
# 英语笔记详情
'''
def english_detail(request, id):
    # 获取对应的English实例 by id
    english_text_detail = get_object_or_404(English, id=id)

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
        audio_url = './media/english/text_to_speech/' + audio_name
        tts = gTTS(text)
        tts.save(audio_url)
        # 并把名字记入数据库
        english_text_detail.audio_name = audio_name
        english_text_detail.save()


    # 需要传递给模板的对象
    context = {
        'english_text_detail': english_text_detail,
        'reference': reference,
        'tag': tag,
        'source': source,
    }

    # 载入模板，并返回context对象
    return render(request, 'detail.html', context)


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
        reference_range = reference.filter(id__in = range(last_reference.id,last_reference.id+10))
        print(reference_range)

    # 如果Table English没有记录。
    else:
        ''' 
        列出页码1-10
        '''
        # 找出书名
        source = Source.objects.get(id=id)
        #
        last_english_text = None
        print(last_english_text)

        last_reference = reference.all().first()
        print(last_reference.id)

        reference_range = reference.all()[0:9]
        print(reference_range)

    #####################################################
    ############# listing Tags #######################
    # ~Q(Tag_id=0)： 所有不等于0的items
    all_tag_list = Tag.objects.filter(~Q(id=0))
    #####################################################

    context = {
        'all_tag_list': all_tag_list,
        'reference_range': reference_range,
        'source': source,
        'last_reference': last_reference,
        'last_english_text': last_english_text
    }
    return render(request, 'input.html', context)


def submit(request):
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
    input_url = "http://127.0.0.1:8000/english/input/"+str(source_id)+"/"


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
    all_tag = request.POST.getlist('tag')
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
    audio_url = './media/english/text_to_speech/' + audio_name
    tts = gTTS(text)
    tts.save(audio_url)
    # 并把名字记入数据库
    english.audio_name = audio_name
    english.save()



    submission_result = "Succeed!"

    if submission_result == "Succeed!":
        time_dalay = 500
        context = {'submission_result': submission_result, 'all_data': all_data, 'input_url': input_url,
                   'time_dalay': time_dalay}
        return render(request, 'submit.html', context)



'''
# word bench
'''
def word_bench(request):

    english = English.objects.filter(~Q(id=0))

    '''
    # 获取keywords
    # 清洗
    '''
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
    # print(word_list)



    '''
    # 获取词性
    # 写入字典
    '''
    # 载入当地的词性分析器
    annotator = StanfordCoreNLP("C:/corenlp", lang="en")
    # 载入在线的词性分析器
    # annotator = StanfordCoreNLP("https://corenlp.run/", lang="en")


    # annotator = CoreNLP(annotators="pos", corenlp_dir=corenlp_dir, lang="en") # 用于CoreNLP
    for item in word_list:
        # 获取词性
        key_word_class = annotator.pos_tag(item)
        # 处理词性数据格式，读出为字符串
        key_word_class = key_word_class[0][1] # 用于StanfordCoreNLP
        # key_word_class = key_word_class[0][1] # 用于CoreNLP

        # 字典的值为空的复合列表:[[],'']。第一个存属于这个键的笔记，第二个存这个键的词性
        # 注入键，并把键对应的词的词性写入值（list类型）中的第二个元素
        word_dict_all.update({item: [[], key_word_class]})

    '''
    # 获取id
    # 写入字典
    '''
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
            # 比对key words，将对应的id装入字典的值中（list的第一个元素（list））。
            if key in item_word_list:
                word_dict_all[key][0].append(item.id)

    # print(word_dict_all)

    '''
    # 对word_dict_all重构得到一个新字典。即，以词性为键，值为keywords和其在数据库中的id。
    '''
    new_dict = {}

    # 获取词性列表
    word_class_list = []
    for key, value in word_dict_all.items():
        word_class_list.append(value[1])

    # 去除重复的词性名称
    word_class_list = list(set(word_class_list))


    #######################################################
    ############ 将老字典重构成新字典，以词性为键################
    ########################################################
    # 新字典形式：其内部结构为：{item: {}}
    # 给字典的键（key）赋值 = 词性
    for item in word_class_list:
        new_dict.update({item: []})  #
    
    # 给字典的值（value）赋值
    # word_dict_all = {'keyword' : [id list], 'word class'}
    # new_dict = {'word class' : { keyword : [id list] } }

    # 遍历新字典，给其相应的键的值赋值
    for new_key, new_value in new_dict.items():
        keyword_id_list = []
        # 把同一词性的英语笔记收集在一起
        for key, value in word_dict_all.items():
            if new_key == value[1]: # value[1] = 'word class'

                # 合并所有相关英语笔记的id
                keyword_id_list.extend(value[0])

        # 去除重复
        keyword_id_list = list(set(keyword_id_list))
        for item in english:
            if item.id in keyword_id_list:
                new_value.append(item)


    vb = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    nn = ['NN', 'NNS', 'NNP', 'NNSP']
    jj = ['JJ', 'JJS', 'JJR']
    rb = ['RB', 'RBS', 'RBR', 'WBR']
    prep_conj = ['IN', 'RP', 'CC', 'TO']
    pronoun = ['PRP', 'WP', 'PRP$', 'WP$']
    determiner = ['DT', 'PDT', 'WDT']
    emo = ['MD', 'UH']
    other = ['CD', 'POS', 'LS', 'SYM', 'EX', 'FW']
    others = pronoun + determiner + emo + other


    context = {
        'english': english,
        'word_dict_all': word_dict_all,
        'new_dict': new_dict,
        'nn': nn,
        'vb': vb,
        'jj': jj,
        'rb': rb,
        'prep_conj': prep_conj,
        'others': others
    }
    return render(request, 'word_bench.html', context)



    #print(word_dict)



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