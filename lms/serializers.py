from django.utils.html import strip_tags
from rest_framework import serializers

from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    content_preview = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            "id",
            "course",
            "title",
            "content",
            "content_preview",
            "video_url",
            "duration_minutes",
            "order",
            "is_published",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_content_preview(self, obj):
        return strip_tags(obj.content)[:200] + "..." if obj.content else ""


class CourseSerializer(serializers.ModelSerializer):
    """
    Вложенный сериализатор курсов: дополнительно возвращаем количество уроков
    и строковое имя инструктора для фронтенда.
    """

    lessons = LessonSerializer(many=True, read_only=True)
    teacher_name = serializers.CharField(source="teacher.get_full_name", read_only=True)
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "description",
            "short_description",
            "preview_image",
            "level",
            "duration_hours",
            "price",
            "is_free",
            "is_published",
            "created_at",
            "updated_at",
            "teacher",
            "teacher_name",
            "lessons",
            "lesson_count",
        )
        read_only_fields = ("id", "created_at", "updated_at", "teacher", "teacher_name", "lesson_count")

    def get_lesson_count(self, obj):
        return obj.lessons.count()

    def create(self, validated_data):
        """
        Метод create вызывается ModelViewSet-ом, поэтому здесь можно безопасно
        назначить инструктора из request.
        """

        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data.setdefault("teacher", request.user)
        return super().create(validated_data)

