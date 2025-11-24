from rest_framework import serializers

from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор урока. Используем ModelSerializer, чтобы DRF автоматически
    генерировал поля и валидацию на основе модели.
    """

    class Meta:
        model = Lesson
        fields = (
            "id",
            "course",
            "title",
            "content",
            "video_url",
            "duration_minutes",
            "order",
            "is_published",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class CourseSerializer(serializers.ModelSerializer):
    """
    Вложенный сериализатор курсов: дополнительно возвращаем количество уроков
    и строковое имя инструктора для фронтенда.
    """

    lessons = LessonSerializer(many=True, read_only=True)
    instructor_name = serializers.CharField(source="instructor.get_full_name", read_only=True)
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
            "instructor",
            "instructor_name",
            "lessons",
            "lesson_count",
        )
        read_only_fields = ("id", "created_at", "updated_at", "instructor", "instructor_name", "lesson_count")

    def get_lesson_count(self, obj):
        return obj.lessons.count()

    def create(self, validated_data):
        """
        Метод create вызывается ModelViewSet-ом, поэтому здесь можно безопасно
        назначить инструктора из request.
        """

        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data.setdefault("instructor", request.user)
        return super().create(validated_data)

