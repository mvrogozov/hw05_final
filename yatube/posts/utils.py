from django.conf import settings
from django.core.paginator import Paginator


def make_pages(request, posts_list):
    paginator = Paginator(posts_list, settings.POSTS_AMOUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
