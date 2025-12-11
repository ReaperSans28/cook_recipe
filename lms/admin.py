from django.contrib import admin
from .models import Course, Lesson, Teacher


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "level", "is_published", "created_at")
    list_filter = ("level", "is_published", "is_free")
    search_fields = ("title", "description")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'is_published', 'created_at']
    list_filter = ['is_published', 'course']
    search_fields = ['title', 'content']
    ordering = ['course', 'order']

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("first_name", "user")
