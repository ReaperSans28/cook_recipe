from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView, get_object_or_404
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from lms.models import Course, Lesson
from lms.paginators import CustomPagination
from lms.serializers import CourseSerializer
from lms.views import IsTeacherOrReadOnly
from users.permissions import IsOwner

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
            .select_related("teacher")
            .prefetch_related("lessons")
        )
        context["latest_lessons"] = (
            Lesson.objects.filter(is_published=True, course__is_published=True)
            .select_related("course")
            .order_by("-created_at")[:6]
        )
        return context


class TeacherRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Простой миксин, который позволяет доступ только пользователям с флагом is_teacher.
    """

    def test_func(self):
        return bool(self.request.user.is_teacher)

    def handle_no_permission(self):
        messages.error(self.request, "Эта страница доступна только авторам курсов.")
        return redirect("home")


class CourseCreateView(TeacherRequiredMixin, CreateView):
    """
    HTML-форма создания курса. Используем ModelForm, чтобы переиспользовать валидацию.
    """

    form_class = CourseForm
    template_name = "landing/course_form.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        course = form.save(commit=False)
        course.teacher = self.request.user
        course.save()
        form.save_m2m()
        messages.success(self.request, "Курс успешно создан. Опубликуйте его через админку или API.")
        self.object = course
        return HttpResponseRedirect(self.get_success_url())


class LessonCreateView(TeacherRequiredMixin, CreateView):
    """
    Страница создания урока. В форме отображаем только курсы текущего инструктора.
    """

    form_class = LessonForm
    template_name = "landing/lesson_form.html"
    success_url = reverse_lazy("home")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["course"].queryset = Course.objects.filter(teacher=self.request.user)
        return form

    def form_valid(self, form):
        lesson = form.save(commit=False)
        if lesson.course.teacher != self.request.user:
            messages.error(self.request, "Можно создавать уроки только в своих курсах.")
            return super().form_invalid(form)
        lesson.save()
        form.save_m2m()
        messages.success(self.request, "Урок сохранён! Не забудьте опубликовать его.")
        self.object = lesson
        return HttpResponseRedirect(self.get_success_url())


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CustomPagination
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]

    def get_template_name(self):
        """Определяет имя шаблона в зависимости от действия"""
        if self.action == 'retrieve':
            return 'landing/course_detail.html'
        elif self.action == 'list':
            return 'course_list.html'
        return 'landing/course_detail.html'

    def retrieve(self, request, *args, **kwargs):
        """Переопределяем для поддержки HTML и JSON"""
        instance = self.get_object()

        if request.accepted_renderer.format == 'html':
            context = {
                'course': instance,
                'user': request.user
            }

            # Проверяем, нужно ли показать форму редактирования
            if request.GET.get('edit') == 'true' and (request.user == instance.teacher or request.user.is_staff):
                return render(request, 'landing/course_form.html', context)

            return Response(context, template_name=self.get_template_name())

        # Для API возвращаем JSON
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='detail-html')
    def detail_html(self, request, pk=None):
        """Альтернативный endpoint для HTML детальной страницы"""
        course = get_object_or_404(Course, pk=pk)
        return render(request, 'landing/course_detail.html', {'course': course})

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = (~IsTeacherOrReadOnly,)
        elif self.action in ['update', 'retrieve']:
            self.permission_classes = (IsTeacherOrReadOnly | IsOwner,)
        elif self.action == 'destroy':
            self.permission_classes = (IsTeacherOrReadOnly | IsOwner,)
        return super().get_permissions()