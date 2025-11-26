from rest_framework import serializers

from .models import Course, Lesson

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = (
            "id",
            "course",
            "title",
            "content",
            "duration_minutes",
            "order",
            "is_published",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "slug",
            "short_description",
            "full_description",
            "avatar",
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

    def get_lesson_count(self, obj):
        return obj.lessons.count()

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data.setdefault("instructor", request.user)
        return super().create(validated_data)
