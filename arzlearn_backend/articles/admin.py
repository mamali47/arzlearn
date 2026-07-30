from django import forms
from django.contrib import admin

from .models import Article, ArticleFAQ, Category, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'order', 'is_active')
    list_filter = ('is_active', 'parent')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class ArticleFAQInline(admin.TabularInline):
    model = ArticleFAQ
    extra = 1
    fields = ('question', 'answer', 'order')


class ArticleAdminForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__'

    def clean_main_tags(self):
        main_tags = self.cleaned_data.get('main_tags')
        if main_tags and main_tags.count() != 3:
            raise forms.ValidationError('باید دقیقاً ۳ تگ اصلی برای مقاله انتخاب شود.')
        return main_tags


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    list_display = (
        'title', 'category', 'status', 'author', 'published_at', 'views_count',
    )
    list_filter = ('status', 'category', 'published_at')
    search_fields = ('title', 'summary', 'body')
    inlines = [ArticleFAQInline]

    class Media:
        css = {'all': ('articles/css/ckeditor-fix.css',)}
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('main_tags', 'secondary_tags')
    date_hierarchy = 'published_at'
    autocomplete_fields = ('category',)
    readonly_fields = ('views_count', 'created_at', 'updated_at')

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'slug', 'category', 'image', 'summary', 'body')
        }),
        ('تگ‌ها', {
            'fields': ('main_tags', 'secondary_tags')
        }),
        ('انتشار', {
            'fields': ('status', 'author', 'published_at', 'reading_time_minutes')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('views_count', 'created_at', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)
