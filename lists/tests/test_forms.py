from django.test import TestCase

from lists.forms import (
    DUPLICATE_ITEM_ERROR, EMPTY_ITEM_ERROR, ExistingListItemForm,
    ItemForm
)
from lists.models import List, Item


class ItemFormTest(TestCase):
    def test_form_renders_item_text_input(self):
        form = ItemForm()

        self.assertIn('placeholder="Enter a to-do item"', form.as_p())
        self.assertIn('class="form-control input-lg"', form.as_p())

    def test_form_validation_for_blank_items(self):
        form = ItemForm(data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['text'],
            [EMPTY_ITEM_ERROR]
        )

    def test_form_save_handles_saving_to_a_list(self):
        _list = List.objects.create()
        form = ItemForm(data={'text': 'hi'})
        new_item = form.save(for_list=_list)

        self.assertEqual(new_item, Item.objects.first())
        self.assertEqual(new_item.text, 'hi')
        self.assertEqual(new_item.list, _list)


class ExistingListItemFormTest(TestCase):
    def test_form_renders_item_text_input(self):
        _list = List.objects.create()
        form = ExistingListItemForm(for_list=_list)
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())

    def test_form_validation_for_blank_items(self):
        _list = List.objects.create()
        form = ExistingListItemForm(for_list=_list, data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['text'],
            [EMPTY_ITEM_ERROR]
        )

    def test_form_validation_for_duplicate_items(self):
        _list = List.objects.create()
        Item.objects.create(list=_list, text='no twins!')
        form = ExistingListItemForm(for_list=_list, data={'text': 'no twins!'})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['text'],
            [DUPLICATE_ITEM_ERROR]
        )

    def test_form_save(self):
        _list = List.objects.create()
        form = ExistingListItemForm(for_list=_list, data={'text': 'hi'})
        new_item = form.save()
        self.assertEqual(new_item, Item.objects.first())
