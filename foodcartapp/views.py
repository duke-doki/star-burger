import json

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
    try:
        data = request.data
        if (
            'products' in data
            and type(data['products']) is list
            and len(data['products']) > 0
        ):
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
        else:
            raise TypeError
    except (AssertionError, TypeError):
        if 'products' not in data:
            message = 'products: Обязательное поле.'
            return Response(message)
        elif type(data['products']) is not list:
            message = (
                f'products: Ожидался list со значениями, '
                f'но был получен {type(data["products"])}.'
            )
        elif not len(data['products']) > 0:
            message = 'products: Этот список не может быть пустым.'
        return Response(message)
