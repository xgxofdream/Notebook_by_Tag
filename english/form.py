# 引入表单类
from django import forms
# 引入文章模型
from .models import English


# 写文章的表单类
class EnglishSubmitForm(forms.ModelForm):
    class Meta:
        # 指明数据模型来源
        model = English
        # 定义表单包含的字段
        fields = ('english_text', 'key_words', 'key_expressions', 'words_to_learn', 'note', 'category', 'tag', 'source')