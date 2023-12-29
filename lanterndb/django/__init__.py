from django.contrib.postgres.operations import CreateExtension
from django.contrib.postgres.indexes import PostgresIndex
from django.db.models import FloatField, Func, Value
from ..utils import to_db


__all__ = ['LanternExtension', 'LanternExtrasExtension', 'L2Distance', 'MaxInnerProduct', 'CosineDistance']


class LanternExtension(CreateExtension):
    def __init__(self):
        self.name = 'lantern'


class LanternExtrasExtension(CreateExtension):
    def __init__(self):
        self.name = 'lantern_extras'


class HnswIndex(PostgresIndex):
    suffix = 'hnsw'

    def __init__(self, *expressions, m=None, ef=None, ef_construction=None, dim=None, **kwargs):
        self.m = m
        self.ef_construction = ef_construction
        self.ef = ef
        self.dim = dim
        super().__init__(*expressions, **kwargs)

    def deconstruct(self):
        path, args, kwargs = super().deconstruct()
        if self.m is not None:
            kwargs['m'] = self.m
        if self.ef is not None:
            kwargs['ef'] = self.ef
        if self.ef_construction is not None:
            kwargs['ef_construction'] = self.ef_construction
        if self.dim is not None:
            kwargs['dim'] = self.dim
        return path, args, kwargs

    def get_with_params(self):
        with_params = []
        if self.m is not None:
            with_params.append('m = %d' % self.m)
        if self.ef is not None:
            with_params.append('ef = %d' % self.ef)
        if self.ef_construction is not None:
            with_params.append('ef_construction = %d' % self.ef_construction)
        if self.dim is not None:
            with_params.append('dim = %d' % self.dim)
        return with_params


class DistanceBase(Func):
    output_field = FloatField()

    def __init__(self, expression, vector, **extra):
        if not hasattr(vector, 'resolve_expression'):
            vector = Value(to_db(vector))
        super().__init__(expression, vector, **extra)


class L2Distance(DistanceBase):
    function = ''
    arg_joiner = ' <-> '


class MaxInnerProduct(DistanceBase):
    function = ''
    arg_joiner = ' <#> '


class CosineDistance(DistanceBase):
    function = ''
    arg_joiner = ' <=> '


class TextEmbedding(Func):
    function = 'text_embedding'

    def __init__(self, model, text, **extra):
        if not hasattr(text, 'resolve_expression'):
            text = Value(text)
        super().__init__(Value(model), text, **extra)


class ImageEmbedding(Func):
    function = 'image_embedding'

    def __init__(self, model, text, **extra):
        if not hasattr(text, 'resolve_expression'):
            text = Value(text)
        super().__init__(Value(model), text, **extra)