import json

import phonenumbers
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order, ProductOrder


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    products = Product.objects.all()
    try:
        data = request.data
        required_keys = [
            "products",
            "firstname",
            "lastname",
            "phonenumber",
            "address",
        ]
        absent_keys = []
        for key in required_keys:
            if key not in data:
                absent_keys.append(key)
            if key == required_keys[-1] and len(absent_keys) > 0:
                message = ', '.join(absent_keys)
                raise TypeError(
                    f'The keys {message} must be presented in the data.'
                )
        for key in required_keys:
            if key == "products":
                if not type(data[key]) is list:
                    raise TypeError(
                        f'products: Ожидался list со значениями, '
                        f'но был получен {data[key]}.'
                    )
                elif not len(data[key]) > 0:
                    raise TypeError(
                        'products: Этот список не может быть пустым.'
                    )
                for product_set in data[key]:
                    if (
                        (
                            'product' not in product_set
                            or 'quantity' not in product_set
                        )
                        or not len(product_set) == 2
                    ):
                        raise TypeError(
                            'products: В этом списке должны быть словари '
                            'с ключами "product" и "quantity"'
                        )
                    elif not (
                        products.filter(id=product_set['product']).exists()
                    ):
                        raise TypeError(
                            f'products: Недопустимый первичный ключ '
                            f'{product_set["product"]}'
                        )
                    elif not (
                        type(product_set['quantity']) is int
                        and product_set['quantity'] > 0
                    ):
                        raise TypeError(
                            f'products: Недопустимый вторичный ключ '
                            f'{product_set["quantity"]}'
                        )
            elif key == "firstname":
                if not type(data[key]) is str:
                    raise TypeError(
                        f'firstname: Ожидался str, '
                        f'но был получен {type(data[key])}.'
                    )
            elif key == "lastname":
                if not type(data[key]) is str:
                    raise TypeError(
                        f'lastname: Ожидался str, '
                        f'но был получен {type(data[key])}.'
                    )
            elif key == "phonenumber":
                try:
                    phone_number = phonenumbers.parse(data[key], "RU")
                except phonenumbers.phonenumberutil.NumberParseException:
                    raise TypeError(
                        "phonenumber': Введен некорректный номер телефона."
                    )
                else:
                    if not phonenumbers.is_valid_number(phone_number):
                        raise TypeError(
                            "phonenumber': Введен некорректный номер телефона."
                        )
            elif key == "address":
                if not type(data[key]) is str:
                    raise TypeError(
                        f'address: Ожидался str, '
                        f'но был получен {type(data[key])}.'
                    )
        order = Order.objects.create(
            firstname=data['firstname'],
            lastname=data['lastname'],
            address=data['address'],
            phonenumber=data['phonenumber']
        )
        for product in data['products']:
            ProductOrder.objects.create(
                order=order,
                product=Product.objects.get(id=product['product']),
                amount=product['quantity']
            )
        return Response(data)
    except (AssertionError, TypeError) as error:
        return Response(str(error))
