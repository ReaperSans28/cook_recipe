from django.contrib import admin

from .models import Course, Lesson, Teacher


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "level", "is_published", "created_at")
    list_filter = ("level", "is_published", "is_free")
    search_fields = ("title", "description")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order", "is_published")
    # list_filter = ("is_published",)
    search_fields = ("title", "course__title")
    autocomplete_fields = ("course",)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("first_name", "user")
