import requests
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum, F
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from geopy import distance

from addresses.models import Place
from fetch_coordinates import fetch_coordinates


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def with_total_cost(self):
        return self.annotate(
            total_cost=Sum(F('products__quantity') * F('products__price'))
        )

    def with_available_restaurants(self):
        return self.annotate(

        )


class Order(models.Model):
    firstname = models.CharField(
        'Имя',
        max_length=50,
        db_index=True
    )
    lastname = models.CharField(
        'Фамилия',
        max_length=50,
        db_index=True
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        db_index=True
    )
    phonenumber = PhoneNumberField(
        'Номер телефона',
        db_index=True,
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=(
            ('Принят', 'Принят'),
            ('Собирается', 'Собирается'),
            ('Доставляется', 'Доставляется'),
            ('Доставлен', 'Доставлен'),
        ),
        default='Принят',
        db_index=True
    )
    comment = models.TextField(
        'Комментарий',
        max_length=200,
        blank=True,
    )
    created_at = models.DateTimeField(
        'Дата создания',
        default=timezone.now,
        db_index=True
    )
    called_at = models.DateTimeField(
        'Дата звонка',
        null=True,
        blank=True
    )
    delivered_at = models.DateTimeField(
        'Дата доставки',
        null=True,
        blank=True
    )
    payment = models.CharField(
        'Способ оплаты',
        max_length=20,
        choices=(
            ('Электронно', 'Электронно'),
            ('Наличностью', 'Наличностью'),
            ('Не указано', 'Не указано')
        ),
        db_index=True,
        default='Не указано',
    )
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='orders',
        verbose_name="Ресторан",
        on_delete=models.CASCADE,
        null=True
    )
    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def available_restaurants(self):
        products_in_order = self.products.select_related('product').all()
        products = [
            product_in_order.product for product_in_order in products_in_order
        ]
        restaurants = []
        places = Place.objects.all()

        for product in products:
            menu_items = product.menu_items.filter(
                availability=True).prefetch_related('restaurant')

            for menu_item in menu_items:
                restaurant_name = menu_item.restaurant.name
                client_address = self.address
                restaurant_coordinates = next(
                    ((place.lat, place.lng) for place in places if
                     place.name == restaurant_name), None)
                client_coordinates = next(
                    ((place.lat, place.lng) for place in places if
                     place.name == client_address), None)

                if not restaurant_coordinates:
                    try:
                        lat, lng = fetch_coordinates(restaurant_name)
                        Place.objects.create(name=restaurant_name, lng=lng,
                                             lat=lat)
                        restaurant_coordinates = lat, lng
                    except (requests.ConnectionError, requests.HTTPError,
                            requests.RequestException) as error:
                        print(f'{error} occurred')

                if not client_coordinates:
                    try:
                        lat, lng = fetch_coordinates(client_address)
                        Place.objects.create(name=client_address, lng=lng,
                                             lat=lat)
                        client_coordinates = lat, lng
                    except (requests.ConnectionError, requests.HTTPError,
                            requests.RequestException) as error:
                        print(f'{error} occurred')

                if restaurant_coordinates and client_coordinates:
                    distance_between = distance.distance(
                        restaurant_coordinates, client_coordinates).km
                    restaurants.append({'name': restaurant_name,
                                        'distance': distance_between})

        unique_restaurants = {r['name']: r['distance'] for r in restaurants}
        sorted_restaurants = sorted(unique_restaurants.items(),
                                    key=lambda x: x[1])

        return ", ".join([f"{name} - {distance} km" for name, distance in
                          sorted_restaurants])

    def __str__(self):
        return f"{self.firstname} {self.lastname} - Заказ {self.pk}"


class ProductOrder(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_products',
        verbose_name='продукт',
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество продукта',
        db_index=True
    )
    price = models.DecimalField(
        'Цена на момент заказа',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        db_index=True
    )
    order = models.ForeignKey(
        Order,
        verbose_name='Заказ',
        on_delete=models.CASCADE,
        related_name='products',
        null=True
    )



