from django.shortcuts import render, redirect

from .models import Item, List
from .forms import ItemForm


def home_page(request):
    return render(request, 'home.html', {'form': ItemForm()})


def view_list(request, list_id):
    _list = List.objects.get(pk=list_id)
    form = ItemForm()

    if request.method == 'POST':
        form = ItemForm(data=request.POST)
        if form.is_valid():
            Item.objects.create(
                text=request.POST['text'],
                list=_list
            )

            return redirect(_list)

    return render(request, 'list.html', {
        'list': _list,
        'form': form,
    })


def new_list(request):
    form = ItemForm(data=request.POST)

    if form.is_valid():
        _list = List.objects.create()
        Item.objects.create(text=request.POST['text'], list=_list)
        return redirect(_list)
    else:
        return render(request, 'home.html', {'form': form})
