from flask_marshmallow import Marshmallow

ma = Marshmallow()


class ProductSchema(ma.Schema):
    """
    Schema that adds meta-data (id, name, description) to model Product.
    """
    class Meta:
        fields = (
            'id',
            'name',
            'description'
        )


class OffersSchema(ma.Schema):
    """
    Schema that adds meta-data (id, price, items in stock) to model Offer.
    """
    class Meta:
        fields = (
            'id',
            'price',
            'items_in_stock'
        )


class OfferSchema(ma.Schema):
    """
    Detailed schema that adds meta-data
    (product name, product description, id, price, items_in_stock)
    to model Offer.
    """
    class Meta:
        fields = (
            'product.name',
            'product.description',
            'id',
            'price',
            'items_in_stock'
        )
