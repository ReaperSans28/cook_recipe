from django import forms

from lms.models import Course, Lesson


class CourseForm(forms.ModelForm):
    """
    Простая модельная форма, которую можно отобразить в шаблоне или на отдельной
    странице. Поля подобраны так, чтобы новичок смог быстро выпустить курс.
    """

    class Meta:
        model = Course
        exclude = ("teacher", "is_published", "created_at", "updated_at")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "short_description": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "preview_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "level": forms.Select(attrs={"class": "form-select"}),
            "duration_hours": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "price": forms.NumberInput(attrs={"class": "form-control", "min": 0, "step": "0.01"}),
            "is_free": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class LessonForm(forms.ModelForm):
    """
    Форма создания урока. Используем Select для выбора курса, чтобы инструктор
    видел только свои программы (фильтрация выполняется во view).
    """

    class Meta:
        model = Lesson
        exclude = ("order", "is_published", "created_at", "updated_at")
        widgets = {
            "course": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "video_url": forms.URLInput(attrs={"class": "form-control"}),
            "duration_minutes": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }


