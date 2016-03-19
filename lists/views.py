from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect

from .models import Item, List


def home_page(request):
    return render(request, 'home.html')


def view_list(request, list_id):
    _list = List.objects.get(pk=list_id)
    error = None

    if request.method == 'POST':
        try:
            item = Item(text=request.POST['item_text'], list=_list)
            item.full_clean()
            item.save()

            return redirect('/lists/%d/' % _list.id)
        except ValidationError:
            error = "You can't have an empty list item"
            pass

    return render(request, 'list.html', {
        'list': _list,
        'error': error,
    })


def new_list(request):
    _list = List.objects.create()
    item = Item(text=request.POST['item_text'], list=_list)

    try:
        item.full_clean()
        item.save()
    except ValidationError:
        _list.delete()
        error = "You can't have an empty list item"
        return render(request, 'home.html', {'error': error})

    return redirect('/lists/%d/' % _list.id)
