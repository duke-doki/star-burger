import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

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


class ProductOrderSerializer(ModelSerializer):
    class Meta:
        model = ProductOrder
        fields = ['quantity', 'product']


class OrderSerializer(ModelSerializer):
    products = ProductOrderSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = [
            'firstname',
            'lastname',
            'address',
            'phonenumber',
            'products'
        ]


@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    order = Order.objects.create(
            firstname=serializer.validated_data['firstname'],
            lastname=serializer.validated_data['lastname'],
            address=serializer.validated_data['address'],
            phonenumber=serializer.validated_data['phonenumber']
        )
    for product in serializer.validated_data['products']:
        ProductOrder.objects.create(
            order=order,
            product=Product.objects.get(id=product['product'].id),
            quantity=product['quantity']
        )
    content = JSONRenderer().render(serializer.data)
    pretty_content = json.loads(content.decode('utf-8'))
    return Response(pretty_content)
