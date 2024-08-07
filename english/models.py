import os
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q

from django.shortcuts import get_object_or_404

#from gtts import gTTS
from boto3 import client

'''
# 全局变量
'''
app = 'english'
# app = 'intelligent_life'


# from stanfordcorenlp import StanfordCoreNLP


'''
# 英语摘录的分类
'''
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name



'''
# 英语摘录的标签
# root sub01-02: 标签的三级所属类别
'''
class Tag(models.Model):
    name = models.CharField(max_length=100)
    root = models.CharField(max_length=100,null=True)
    sub01 = models.CharField(max_length=100,null=True)
    sub02 = models.CharField(max_length=100,null=True)

    def tag_list(self, id):

        if id == 0:
            # ~Q(source_id=0)： 所有不等于0的items
            all_tag_list = Tag.objects.filter(~Q(id=id))

        # 初始化一个字典
        tag_dict = {}
        # 将数据表转化成字典。注意，item.root重复的键只会保留一个。所以，要对字典的键的值补救。
        for item in all_tag_list:
            # list([item.sub01]):将item.sub01转化为完整不分割的列表
            tag_dict.update({item.root: list([item.sub01])})

        for every_key in tag_dict:
            for item in all_tag_list:
                if every_key == item.root:
                    tag_dict[every_key].append(item.sub01)
            # 字典的值去重
            tag_dict[every_key] = list(set(tag_dict[every_key]))

        return {
            'all_tag_list': all_tag_list,
            'tag_dict': tag_dict,
        }



    def __str__(self):
        return self.name


''''''


# 英语笔记的来源

class Source(models.Model):

    name = models.CharField(max_length=100)
    format = models.CharField(max_length=100,null=True)
    type = models.CharField(max_length=100)
    author = models.CharField(max_length=1000,null=True)
    summary = models.TextField(null=True)
    publication = models.TextField(null=True)


    def source_summary(self):

        source = Source.objects.filter(~Q(id=0))

        '''Summary Table Source'''
        source_dict = {}

        for item in source:
            if source_dict.__contains__(item.type):
                # 计数
                source_dict[item.type][0] = source_dict[item.type][0] + 1
                # 记录source id, 其一一对应于name字段
                source_dict[item.type][1].append(str(item.id))
            else:
                count = 1
                source_id_list = list([str(item.id)])

                source_dict.update({item.type: [count, source_id_list]})

        return source_dict


    def source_list(self, source_type):

        source = Source.objects.filter(~Q(id=0))

        if source_type == 'all':
            source = source
        else:
            source = source.filter(type=source_type)

        return source



    def __str__(self):
        return self.name


'''
# 英语笔记的引用详情
'''
class Reference(models.Model):

    english_text_location = models.CharField(max_length=100)
    note = models.TextField(null=True)

    source = models.ForeignKey(Source, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.english_text_location


'''
# 英语笔记的整理归纳
'''
class Summary(models.Model):

    title = models.CharField(max_length=100, null=True)
    abstract = models.TextField(null=True)
    summary = models.TextField(null=True)

    def __str__(self):
        return self.title


'''
# 英语摘录
'''
class English(models.Model):
    # 摘录的英文
    english_text = models.TextField()

    # 这两个列分别表示英文摘录的创建时间和最后一次修改时间，存储时间的字段用 DateTimeField 类型。
    created_time = models.DateTimeField(null=True)
    modified_time = models.DateTimeField(null=True)

    # 笔记
    key_words = models.TextField(null=True)
    key_expressions = models.TextField(null=True)
    words_to_learn = models.TextField(null=True)
    note = models.TextField(null=True)

    # 是否生成了音频
    audio_name = models.CharField(max_length=255, null=True)



    # 这是分类，标签和来源。
    # 我们在这里把文章对应的数据库表和分类、标签对应的数据库表关联了起来，但是关联形式稍微有点不同。
    # 我们规定一篇文章只能对应一个分类，但是一个分类下可以有多篇文章，所以我们使用的是 ForeignKey，即一
    # 对多的关联关系。且自 django 2.0 以后，ForeignKey 必须传入一个 on_delete 参数用来指定当关联的
    # 数据被删除时，被关联的数据的行为。
    # 我们这里假定当某个分类被删除时，该分类下全部文章也同时被删除，因此使用 on_delete=models.CASCADE 参数，意为级联删除。

    # 而对于标签来说，一篇文章可以有多个标签，同一个标签下也可能有多篇文章，所以我们使用
    # ManyToManyField，表明这是多对多的关联关系。
    # 同时我们规定文章可以没有标签，因此为标签 tags 指定了 blank=True。指定 CharField 的 blank=True 参数值后就可以允许空值了。
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    tag = models.ManyToManyField(to=Tag, related_name="notes", null=True)
    summary = models.ManyToManyField(to=Tag, related_name="summary_notes", null=True)

    reference = models.ForeignKey(Reference, on_delete=models.CASCADE, null=True)

    image_id = models.CharField(max_length=255, null=True)
    video_id = models.CharField(max_length=255, null=True)

    # 作者。这里 User 是从 django.contrib.auth.models 导入的。
    # django.contrib.auth 是 django 内置的应用，专门用于处理网站用户的注册、登录等流程，User 是
    # django 为我们已经写好的用户模型。
    # 这里我们通过 ForeignKey 把文章和 User 关联了起来。
    # 因为我们规定一篇文章只能有一个作者，而一个作者可能会写多篇文章，因此这是一对多的关联关系，和
    # Category 类似。
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    #@staticmethod
    def key_words_clean(self, text):
        '''
        # 清洗
        '''
        word_str = ''

        if text:
            word_str = word_str + text + ','

            # 转化为list via 逗号
            word_list = word_str.split(',')

            # 去掉list中的空值（因为有的笔记里面，我没有输入key words）
            while '' in word_list:
                word_list.remove('')

            # 去掉空格（录入时手误有时候会带上空格）
            for i in range(len(word_list)):
                word_list[i] = word_list[i].replace(' ', '')

            # 去掉重复的元素
            word_list = list(set(word_list))
        else:
            word_list = ''

        return word_list

    #@staticmethod
    def key_expressions_clean(self, text):
        '''
        # 清洗
        '''
        word_str = ''
        if text:
            word_str = word_str + text + ','
            # 转化为list via 逗号
            word_list = word_str.split(',')

            # 去掉list中的空值（因为有的笔记里面，我没有输入key words）
            while '' in word_list:
                word_list.remove('')
            # 去掉重复的元素
            word_list = list(set(word_list))
        else:
            word_list = ''

        return word_list

   # @staticmethod
    def text_highlight(self, item):

        # 把笔记中的key_words 和 key_expressions高亮显示出来
        # 1. 把<mark style>, <span style> 加进笔记
        # 2. 把笔记数据装进字典

        english_dict = {};

        # 初始化english_text
        english_text = item.english_text
        # 清洗字符串，并转化成list
        keyword_list = item.key_words_clean(item.key_words)
        key_expression_list = item.key_expressions_clean(item.key_expressions)

        '''把笔记中的key_expressions高亮显示出来'''
        for i in range(len(key_expression_list)):
            # 把笔记中的key_expressions加上<mark style>
            styled_key_expression = "<mark>" + key_expression_list[i] + "</mark>"
            # 替换掉english_text无<mark style>标记的key_expressions
            english_text = english_text.replace(key_expression_list[i], styled_key_expression)


        '''把笔记中的key_words高亮显示出来'''
        for i in range(len(keyword_list)):
            # 把笔记中的key_word加上<span style>
            styled_key_words = '<span>' + keyword_list[i] + '</span>'
            # 替换掉english_text无<span style>标记的key_words
            english_text = english_text.replace(keyword_list[i], styled_key_words)

        '''笔记的其他数据'''
        item_image = Image()
        item_video = Video()
        if item.image_id:
            item_image = get_object_or_404(Image, id=item.image_id)
        if item.video_id:
            item_video = get_object_or_404(Video, id=item.video_id)

        '''把笔记数据装进字典'''
        key = item.id
        value = {
            'english_text': english_text,
            'key_words': item.key_words,
            'key_expressions': item.key_expressions,

            'audio_name': item.audio_name,

            'image_name': item_image.image_name,
            'video_name': item_video.video_name,

            'video_to_mp3_name': item_video.video_to_mp3,
        }

        english_dict.update({key: value})

        return english_dict

    '''
    # word bench
    '''

    def word_bench(self, method, value):

        if method == 'source':

            if value == 'all':
                english = English.objects.filter(~Q(id=0))
            # 即，反向查询。
            else:
                source_id = Source.objects.filter(type=value).values('id')
                reference = Reference.objects.filter(source_id__in=source_id)
                reference_id = reference.values('id')

                english = English.objects.filter(reference_id__in=reference_id)

        if method == 'tag':
            english = English.objects.filter(id__in=value)



        '''
        # 获取keywords
        # 清洗
        '''
        word_dict_all = {}

        word_list = []
        for item in english:
            word_list = word_list + item.key_words_clean(item.key_words)

        # 去掉list中的空值
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
            key_word_class = key_word_class[0][1]  # 用于StanfordCoreNLP
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
                if new_key == value[1]:  # value[1] = 'word class'

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
        return context



    '''
    # 正向查询 English to Source
    '''
    def english_to_source(self, english):
        '''
        if isinstance(english_id_list, list):
            english_id_list = english_id_list
        # 一条英语笔记的查询时，english_id_list为整数，所以要转化为list
        else:
            english_id_list = list(str(english_id_list))

        # 获取 id，获取笔记
        english = English.objects.filter(id__in=english_id_list)
        '''

        # 初始化 字典的结构{int:{int:int}}
        dict_english_to_source = {}
        # 初始化 字典的结构{int:[int, []]}
        statistics_source = {}


        english_styled = {};

        if english:
            # 收集信息
            for english_item in english:
                # 收集english-source对应关系
                reference = english_item.reference
                source = reference.source
                dict_english_to_source.update({english_item.id:{reference.id:source.id}})

                # 调用
                # 把笔记中的key_words 和 key_expressions高亮显示出来 via English的功能：text_highlight
                single_english_note = english_item.text_highlight(english_item)
                english_styled.update(single_english_note)

                # 统计source的情况
                if statistics_source.__contains__(source.name):
                    # 计数
                    statistics_source[source.name][0] = statistics_source[source.name][0] + 1
                    # 记录对应的笔记id
                    statistics_source[source.name][1].append(str(english_item.id))
                    # 记录对应的笔记的source_type
                    statistics_source[source.name][2] =source.type
                else:
                    count = 1
                    english_id_list = list([str(english_item.id)])
                    source_type = source.type

                    statistics_source.update({source.name: [count, english_id_list, source_type]})

        else:
            reference = None
            english_styled = None
            source = None
            dict_english_to_source = None
            statistics_source = None

        data = {
            'reference': reference,
            'english': english,
            'english_styled': english_styled,
            'source': source,
            'dict_english_to_source': dict_english_to_source,
            'statistics_source': statistics_source,
        }
        return data

    '''
    # 正向查询 English to Tag
    '''
    def english_to_tag(self, english):
        '''
        if isinstance(english_id_list, list):
            english_id_list = english_id_list
        # 一条英语笔记的查询时，english_id_list为整数，所以要转化为list
        else:
            english_id_list = list(str(english_id_list))

        # 获取 id，获取笔记
        english = English.objects.filter(id__in=english_id_list)
        '''

        # 初始化 字典的结构{int:{int:int}}
        dict_english_to_tag = {}
        # 初始化 字典的结构{int:[int, []]}
        statistics_tag = {}

        for english_item in english:
            # 收集english-tags对应关系
            tag = english_item.tag.all()

            dict_english_to_tag.update({english_item.id:tag})
            # print(tag)


            # 统计tags的情况
            for tag_item in tag:
                # print(tag_item)
                if statistics_tag.__contains__(tag_item.name):
                    # 计数
                    statistics_tag[tag_item.name][0] = statistics_tag[tag_item.name][0] + 1
                    # 记录对应的笔记id
                    statistics_tag[tag_item.name][1].append(str(english_item.id))

                else:
                    count = 1
                    english_id_list = list([str(english_item.id)])

                    statistics_tag.update({tag_item.name: [count, english_id_list]})

            # print(statistics_tag)



        data = {
            'english': english,
            'dict_english_to_tag': dict_english_to_tag,
            'statistics_tag': statistics_tag,
        }

        return data

    '''
    # 反向查询 Source to English
    '''
    def source_to_english(self, source_id_list):

        if isinstance(source_id_list, list):
            source_id_list = source_id_list
        # 一条记录的查询时，source_id_list为整数，所以要转化为list
        else:
            # [str(source_id_list)]一定要加个方括号，这样两位数就不会被list成两个元素了，比如10就不会变成[1,0]
            source_id_list = list([str(source_id_list)])

        source = Source.objects.filter(id__in=source_id_list)

        # Reference的__str__一定要放回str类型的数据，不然报错！很奇怪！
        reference = Reference.objects.filter(source_id__in=source_id_list)
        reference_id = reference.values('id')

        english = English.objects.filter(reference_id__in=reference_id)



        if english:

            # 调用
            # 把笔记中的key_words 和 key_expressions高亮显示出来 via English的功能：text_highlight
            english_styled = {};



            for item in english:
                single_english_note = item.text_highlight(item)
                english_styled.update(single_english_note)

        else:
            english_styled = None


        # 整理English by Reference
        # 字典 dict_english_sorted_by_reference 的结构 {str:{int:{}}
        # single_english_note 是字典类型
        dict_english_sorted_by_reference = {}


        for english_item in english:

            if dict_english_sorted_by_reference.__contains__(english_item.reference):

                single_english_note = english_item.text_highlight(english_item)
                dict_english_sorted_by_reference[english_item.reference].update({english_item.id: single_english_note})

            else:
                single_english_note = english_item.text_highlight(english_item)

                english_id_text = {english_item.id: single_english_note}
                dict_english_sorted_by_reference.update({english_item.reference: english_id_text})


        data = {
            'source': source,
            'reference': reference,
            'english': english,
            'english_styled': english_styled,
            'dict_english_sorted_by_reference': dict_english_sorted_by_reference,

        }
        return data


    '''
    # 反向查询 Tag to English
    '''
    def tag_to_english(self, tag_id_list, intersect_or_not):

        if isinstance(tag_id_list, list):
            tag_id_list = tag_id_list
        # 一条记录的查询时，tag_id_list为整数，所以要转化为list
        else:
            # [str(tag_id_list)]一定要加个方括号，这样两位数就不会被list成两个元素了，比如10就不会变成[1,0]
            tag_id_list = list([str(tag_id_list)])

        # 实例化Tag
        tag_set = Tag.objects.filter(id__in=tag_id_list)

        arr_query = tag_id_list

        for index in range(len(tag_id_list)):
            tag_obj = Tag.objects.get(id=tag_id_list[index])

            all_english_text = tag_obj.notes.all()

            arr_query[index] = all_english_text

        ''''''
        # Tag的交集/并集运算
        if intersect_or_not == 'no':
            for index in range(len(arr_query)):
                all_english_text = all_english_text | arr_query[index]

        if intersect_or_not == 'yes':
            for index in range(len(arr_query)):
                all_english_text = all_english_text & arr_query[index]

        # 去除重复items
        all_english_text = all_english_text.order_by('id').distinct()

        english_id_list = []
        for item in all_english_text:
            english_id_list.append(str(item.id))


        # 把笔记中的key_words 和 key_expressions高亮显示出来 via English的功能：text_highlight
        english_styled = {};
        for item in all_english_text:
            single_english_note = item.text_highlight(item)
            english_styled.update(single_english_note)

        # 需要传递给模板的对象
        data = {
            'all_english_text': all_english_text,
            'english_id_list': english_id_list,
            'intersect_or_not': intersect_or_not,
            'tag_set': tag_set,
            'english_styled': english_styled,
        }

        return data


    '''
    # 创建文件夹
    '''
    def create_folder(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            print('This folder exists!')

    '''
    # 创建语音文件
    '''
    def create_audio(self, audio_src, source_id, tag, element, english):
        ''''''
        # 调用 Amazon Polly
        polly = client(
            "polly",
            aws_access_key_id='',
            aws_secret_access_key='',
            region_name="us-east-1"
            )

        conversion_level = 'neural'

        # Joanna represents a female voice with newscaster speaking style
        # Matthew represents a female voice with newscaster speaking style
        # Joey represents a male voice
        # Refer to https://zhuanlan.zhihu.com/p/572962199 for more
        voice_style = 'Matthew'
        audio_farmat = 'mp3'



        # 语音文件存储地址
        audio_src = audio_src


        if english and not element:
            text = english.english_text
            audio_name = str(source_id) + '-' + str(english.id) + '.mp3'
            audio_file_location = audio_src + audio_name


            ''''''
            # 语音合成 via Amazon Polly and boto3
            response=polly.synthesize_speech(Text=text,OutputFormat=audio_farmat, Engine=conversion_level, VoiceId=voice_style)
            file = open(audio_file_location, 'wb')
            file.write(response['AudioStream'].read())
            file.close()

            '''
            # 语音合成
            tts = gTTS(text)

            # 语音保存
            tts.save(audio_file_location)
            '''

            # 并把名字记入数据库
            english.audio_name = audio_name
            english.save()

        if english and element:

            text = element.text
            audio_name = str(source_id) + '-' + str(english.id) + '-' + str(element.id) + '-' + str(tag.id) + '.mp3'
            audio_file_location = audio_src + audio_name

            ''''''
            # 语音合成 via Amazon Polly and boto3
            response=polly.synthesize_speech(Text=text,OutputFormat=audio_farmat, Engine=conversion_level, VoiceId=voice_style)
            file = open(audio_file_location, 'wb')
            file.write(response['AudioStream'].read())
            file.close()


            '''
            # 语音合成
            tts = gTTS(text)

            # 语音保存
            tts.save(audio_file_location)
            '''

            # 并把名字记入数据库
            element.audio_name = audio_name
            element.save()


        return audio_file_location


    '''
    # 删除语音文件
    '''
    def delete_audio(self, target, english, folder_location):

        if target == 'del_english':
            audio_location = folder_location + english.audio_name
            os.remove(audio_location)

        if target == 'del_element':

            element = Element.objects.filter(english_id=english.id).values('audio_name')

            for item in element:
                if item['audio_name']:
                    audio_location = folder_location + item['audio_name']
                    if os.path.exists(audio_location):
                        os.remove(audio_location)
                    print(audio_location)


    def __str__(self):
        return self.english_text


'''
# 来自图片的英语摘录
'''
class Image(models.Model):

    english = models.ForeignKey(English, on_delete=models.CASCADE, null=True)

    description = models.TextField(null=True)
    capture_location = models.CharField(max_length=1000, null=True)

    # 这两个列分别表示英文摘录的创建时间和最后一次修改时间，存储时间的字段用 DateTimeField 类型。
    created_time = models.DateTimeField(null=True)
    modified_time = models.DateTimeField(null=True)

    image_name = models.ImageField(null=True, upload_to=app + '/image')

'''
# 来自视频的英语摘录
'''
class Video(models.Model):

    english = models.ForeignKey(English, on_delete=models.CASCADE, null=True)

    description = models.TextField(null=True)
    capture_location = models.CharField(max_length=1000,null=True)

    # 从视频中提取的声音的存储位置
    video_to_mp3 = models.CharField(max_length=1000,null=True)

    # 从视频中提取的声音的转化成文本
    video_to_mp3_to_text = models.CharField(max_length=1000,null=True)

    # 这两个列分别表示英文摘录的创建时间和最后一次修改时间，存储时间的字段用 DateTimeField 类型。
    created_time = models.DateTimeField(null=True)
    modified_time = models.DateTimeField(null=True)

    # 上传的视频的存储位置
    video_name = models.FileField(null=True,upload_to = app + '/video')

'''
# 英语摘录的单词和表达
'''
class Element(models.Model):
    text = models.TextField(null=True)
    type = models.CharField(max_length=100) ## key_words, Key_expressions
    english = models.ForeignKey(English, on_delete=models.CASCADE, null=True)
    tag = models.ManyToManyField(to=Tag, related_name="for_element", null=True)
    note = models.TextField(null=True)
    # 是否有音频
    audio_name = models.CharField(max_length=1000, null=True)

    '''
     # 反向查询 Tag to Element
     '''

    def tag_to_element(self, tag_id_list, intersect_or_not):

        if isinstance(tag_id_list, list):
            tag_id_list = tag_id_list
        # 一条记录的查询时，tag_id_list为整数，所以要转化为list
        else:
            # [str(tag_id_list)]一定要加个方括号，这样两位数就不会被list成两个元素了，比如10就不会变成[1,0]
            tag_id_list = list([str(tag_id_list)])

        # 实例化Tag
        tag_set = Tag.objects.filter(id__in=tag_id_list)

        arr_query = tag_id_list

        for index in range(len(tag_id_list)):
            tag_obj = Tag.objects.get(id=tag_id_list[index])

            #用到 tag = models.ManyToManyField(to=Tag, related_name="for_element", null=True)
            all_element_text = tag_obj.for_element.all()

            arr_query[index] = all_element_text

        ''''''
        # Tag的交集/并集运算
        if intersect_or_not == 'no':
            for index in range(len(arr_query)):
                all_element_text = all_element_text | arr_query[index]

        if intersect_or_not == 'yes':
            for index in range(len(arr_query)):
                all_element_text = all_element_text & arr_query[index]

        # 去除重复items
        all_element_text = all_element_text.order_by('id').distinct()



        # 初始化 字典的结构{element_id:}
        dict_element = {}

        element_id_list = []
        for item in all_element_text:
            element_id_list.append(str(item.id))
            english = English.objects.get(id=item.english_id)
            reference = english.reference
            source = reference.source

            #tag = item.tag.all()
            #dict_element.update({item: [tag, english, source]})
            dict_element.update({item: {english: source}})





        # 需要传递给模板的对象
        data = {
            'all_element_text': all_element_text,
            'element_id_list': element_id_list,
            'intersect_or_not': intersect_or_not,
            'tag_set': tag_set,
            'dict_element': dict_element,
        }

        return data


    '''
    # 反向查询 Element to English
    '''
    def element_to_english(self, element_id_list):

        if isinstance(element_id_list, list):
            element_id_list = element_id_list
        # 一条记录的查询时，element_id_list为整数，所以要转化为list
        else:
            # [str(element_id_list)]一定要加个方括号，这样两位数就不会被list成两个元素了，比如10就不会变成[1,0]
            element_id_list = list([str(element_id_list)])

        element = Element.objects.filter(id__in=element_id_list)
        english_id = element.values('english_id')
        #print(english_id)
        english = English.objects.filter(id__in=english_id)
        #print(english)


        # 调用
        # 把笔记中的key_words 和 key_expressions高亮显示出来 via English的功能：text_highlight
        english_styled = {};

        for item in english:
            single_english_note = item.text_highlight(item)
            #print(single_english_note)
            reference = item.reference
            source = reference.source

            english_styled.update({item: [single_english_note, source]})

        # print(english_styled)
        data = {
            'element': element,
            'english': english,
            'english_styled': english_styled,

        }
        return data


    '''
    # 正向查询 English to Element
    '''
    def english_to_element(self, english):

        english_id = english.id
        element = Element.objects.filter(english_id=english_id).order_by('id')
        return element

    def element_to_tag(self, element):

        # 初始化 字典的结构{int:{int:int}}
        dict_element_to_tag = {}
        # 初始化 字典的结构{int:[int, []]}
        statistics_tag = {}
        # 初始化 字典的结构{str:{int:str}}
        dict_element_sorted_by_tag = {}

        for element_item in element:
            #收集element-source对应关系
            english = English.objects.get(id=element_item.english_id)
            reference = english.reference
            source = reference.source


            # 收集element-tags对应关系
            tag = element_item.tag.all()
            tag_list = []
            for tag_item in tag:
                tag_list.append(tag_item.name)

            while '' in tag_list:
                tag_list.remove('')

            dict_element_to_tag.update({element_item.id: [element_item.text,element_item.type,tag_list]})
            #print(tag)

            # 统计tags的情况
            for tag_item in tag:
                #print(tag_item)
                if statistics_tag.__contains__(tag_item.name):
                    # 计数
                    statistics_tag[tag_item.name][0] = statistics_tag[tag_item.name][0] + 1
                    # 记录对应的element id
                    statistics_tag[tag_item.name][1].append(str(element_item.id))
                    # 记录对应的element text
                    statistics_tag[tag_item.name][2] = statistics_tag[tag_item.name][2] + element_item.text + ','

                else:
                    count = 1
                    element_id_list = list([str(element_item.id)])
                    element_text_str = element_item.text + ','

                    statistics_tag.update({tag_item.name: [count, element_id_list, element_text_str]})

            # print(statistics_tag)

            # 整理elements by tag
            # 字典 dict_element_sorted_by_tag 的结构 {str:{int:[]}}
            for tag_item in tag:
                #print(tag_item)
                if dict_element_sorted_by_tag.__contains__(tag_item.name):

                    dict_element_sorted_by_tag[tag_item.name].update({element_item.audio_name: [element_item.text,element_item.english_id,source.id]})


                else:
                    element_id_text = {element_item.audio_name: [element_item.text,element_item.english_id,source.id]}

                    dict_element_sorted_by_tag.update({tag_item.name: element_id_text})

            # print(dict_element_sorted_by_tag)

        data = {
            'element': element,
            'dict_element_to_tag': dict_element_to_tag,
            'statistics_tag': statistics_tag,
            'dict_element_sorted_by_tag': dict_element_sorted_by_tag,

        }

        return data

    def __str__(self):
        return self.text