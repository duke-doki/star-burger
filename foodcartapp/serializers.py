from rest_framework.serializers import ModelSerializer

from foodcartapp.models import ProductOrder, Order


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

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        for product_data in products_data:
            ProductOrder.objects.create(
                order=order,
                **product_data
            )
        return order
