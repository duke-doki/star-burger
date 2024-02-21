from rest_framework.serializers import ModelSerializer

from foodcartapp.models import ProductOrder, Order, Product


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
            product_here = Product.objects.select_for_update().get(
                id=product_data['product'].id)
            ProductOrder.objects.create(
                order=order,
                product=product_here,
                quantity=product_data['quantity'],
                price=product_here.price
            )
        return order
