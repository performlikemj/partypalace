from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Theme

def theme_list(request):
    queryset = Theme.objects.order_by('name')
    paginator = Paginator(queryset, 6)  # show 6 themes per page
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)

    return render(request, 'themes/theme_list.html', {'page_obj': page_obj})

def theme_detail(request, slug):
    theme = get_object_or_404(Theme, slug=slug)
    return render(request, 'themes/theme_detail.html', {'theme': theme})
