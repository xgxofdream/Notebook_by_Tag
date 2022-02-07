from django.db import models
from django.contrib.auth.models import User

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
    reference = models.ForeignKey(Reference, on_delete=models.CASCADE, null=True)

    # 作者。这里 User 是从 django.contrib.auth.models 导入的。
    # django.contrib.auth 是 django 内置的应用，专门用于处理网站用户的注册、登录等流程，User 是
    # django 为我们已经写好的用户模型。
    # 这里我们通过 ForeignKey 把文章和 User 关联了起来。
    # 因为我们规定一篇文章只能有一个作者，而一个作者可能会写多篇文章，因此这是一对多的关联关系，和
    # Category 类似。
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.english_text



