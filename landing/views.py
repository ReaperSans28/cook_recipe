from django.views.generic import TemplateView


from .models import Course

class HomeView(TemplateView):
    """
    Обычный Django TemplateView для отображения главной страницы.

    Это не DRF view, потому что мы хотим показывать HTML страницу,
    а не JSON ответ. DRF используется для API endpoints.
    """
    template_name = "landing/index.html"

    def get_context_data(self, **kwargs):
        """
        Добавляем данные в контекст шаблона.

        Получаем последние книги и новости для отображения на главной странице.
        """
        context = super().get_context_data(**kwargs)
        # Получаем последние 6 книг
        context["books"] = Course.objects.all()[:6]
        return context
