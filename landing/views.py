from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from lms.models import Course, Lesson

from .forms import CourseForm, LessonForm


class HomeView(TemplateView):
    """
    Главная страница платформы. Показываем подборку курсов и свежие уроки.
    """

    template_name = "landing/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["courses"] = (
            Course.objects.filter(is_published=True)
            .select_related("instructor")
            .prefetch_related("lessons")
        )[:9]
        context["latest_lessons"] = (
            Lesson.objects.filter(is_published=True, course__is_published=True)
            .select_related("course")
            .order_by("-created_at")[:6]
        )
        return context


class InstructorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Простой миксин, который позволяет доступ только пользователям с флагом is_instructor.
    """

    def test_func(self):
        return bool(self.request.user.is_instructor)

    def handle_no_permission(self):
        messages.error(self.request, "Эта страница доступна только авторам курсов.")
        return redirect("home")


class CourseCreateView(InstructorRequiredMixin, CreateView):
    """
    HTML-форма создания курса. Используем ModelForm, чтобы переиспользовать валидацию.
    """

    form_class = CourseForm
    template_name = "landing/course_form.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        course = form.save(commit=False)
        course.instructor = self.request.user
        course.save()
        form.save_m2m()
        messages.success(self.request, "Курс успешно создан. Опубликуйте его через админку или API.")
        self.object = course
        return HttpResponseRedirect(self.get_success_url())


class LessonCreateView(InstructorRequiredMixin, CreateView):
    """
    Страница создания урока. В форме отображаем только курсы текущего инструктора.
    """

    form_class = LessonForm
    template_name = "landing/lesson_form.html"
    success_url = reverse_lazy("home")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["course"].queryset = Course.objects.filter(instructor=self.request.user)
        return form

    def form_valid(self, form):
        lesson = form.save(commit=False)
        if lesson.course.instructor != self.request.user:
            messages.error(self.request, "Можно создавать уроки только в своих курсах.")
            return super().form_invalid(form)
        lesson.save()
        form.save_m2m()
        messages.success(self.request, "Урок сохранён! Не забудьте опубликовать его.")
        self.object = lesson
        return HttpResponseRedirect(self.get_success_url())