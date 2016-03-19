from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase

from lists.views import home_page
from lists.models import Item, List


class HomePageTest(TestCase):
    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = home_page(request)
        expected_html = render_to_string('home.html', request=request)

        self.assertEqual(response.content.decode(), expected_html)


class ListAndItemModelTest(TestCase):
    def test_saving_and_retrieving_items(self):
        _list = List()
        _list.save()

        first_item = Item()
        first_item.text = 'The first (ever) list item'
        first_item.list = _list
        first_item.save()

        second_item = Item()
        second_item.text = 'Item the second'
        second_item.list = _list
        second_item.save()

        saved_list = List.objects.first()
        self.assertEqual(_list, saved_list)

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]

        self.assertEqual(first_saved_item.text, 'The first (ever) list item')
        self.assertEqual(first_saved_item.list, _list)
        self.assertEqual(second_saved_item.text, 'Item the second')
        self.assertEqual(second_saved_item.list, _list)


class ListViewTest(TestCase):
    def test_uses_list_template(self):
        _list = List.objects.create()
        response = self.client.get('/lists/%d/' % _list.id)
        self.assertTemplateUsed(response, 'list.html')

    def test_displays_only_items_for_that_list(self):
        first_list = List.objects.create()
        Item.objects.create(text='itemey 1', list=first_list)
        Item.objects.create(text='itemey 2', list=first_list)

        second_list = List.objects.create()
        Item.objects.create(text='itemey 3', list=second_list)
        Item.objects.create(text='itemey 4', list=second_list)

        response = self.client.get('/lists/%d/' % first_list.id)

        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')
        self.assertNotContains(response, 'itemey 3')
        self.assertNotContains(response, 'itemey 4')

    def test_passed_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get('/lists/%d/' % correct_list.id)
        self.assertEqual(response.context['list'], correct_list)


class NewListTest(TestCase):
    def test_saving_a_POST_request(self):
        self.client.post('/lists/new', data={
            'item_text': 'A new list item'
        })

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_redirects_after_POST(self):
        response = self.client.post('/lists/new', data={
            'item_text': 'A new list item'
        })

        _list = List.objects.first()

        self.assertRedirects(response, '/lists/%d/' % _list.id)


class NewItemTest(TestCase):
    def test_can_save_a_POST_request_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            '/lists/%d/add_item' % correct_list.id,
            data={'item_text': 'A new item'}
        )

        self.assertEqual(Item.objects.count(), 1)
        item = Item.objects.first()

        self.assertEqual(item.text, 'A new item')
        self.assertEqual(item.list, correct_list)

    def test_redirects_to_list_view(self):
        _list = List.objects.create()

        response = self.client.post(
            '/lists/%d/add_item' % _list.id,
            data={'item_text': 'A new item'}
        )

        self.assertRedirects(response, '/lists/%d/' % _list.id)
