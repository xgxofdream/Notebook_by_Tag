from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q

from stanfordcorenlp import StanfordCoreNLP

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


    def source_list(self, id):
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
        if id == 9:
            source = source.filter(type='Review Papers')
            source_type = "Review Papers"
        if id == 10:
            source = source.filter(type='Research Papers')
            source_type = "Research Papers"

        return {
            'source': source,
            'source_type': source_type,
        }



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

    # 是否有音频
    audio_name = models.CharField(max_length=100, null=True)

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

        return word_list

    #@staticmethod
    def key_expressions_clean(self, text):
        '''
        # 清洗
        '''
        word_str = ''
        word_str = word_str + text + ','
        # 转化为list via 逗号
        word_list = word_str.split(',')

        # 去掉list中的空值（因为有的笔记里面，我没有输入key words）
        while '' in word_list:
            word_list.remove('')


        # 去掉重复的元素
        word_list = list(set(word_list))

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

        '''把笔记数据装进字典'''
        key = item.id
        value = {
            'english_text': english_text,
            'key_words': item.key_words,
            'key_expressions': item.key_expressions,
            'audio_name': item.audio_name,
        }

        english_dict.update({key: value})

        return english_dict

    '''
    # word bench
    '''

    def word_bench(self, type, id):

        if type == 'source':
            if id == 0:
                english = English.objects.filter(~Q(id=0))
            else:
                # Reference的__str__一定要放回str类型的数据，不然报错！很奇怪！
                reference = Reference.objects.filter(source_id=id)
                reference_id = reference.values('id')

                english = English.objects.filter(reference_id__in=reference_id)

        if type == 'tag':
            english = English.objects.filter(id__in=id)



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
        print(word_list)

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



    def __str__(self):
        return self.english_text



