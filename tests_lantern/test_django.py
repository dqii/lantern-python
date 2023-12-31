import os
import django
from django.conf import settings
from django.core import serializers
from django.db import connection, migrations, models
from django.db.models import Avg, Sum
from django.contrib.postgres.fields import ArrayField
from django.db.migrations.loader import MigrationLoader
from django.forms import ModelForm
from math import sqrt
import numpy as np
from lantern_django import LanternExtension, LanternExtrasExtension, HnswIndex, L2Distance, CosineDistance, RealField
from unittest import mock

settings.configure(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'postgres'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
)
django.setup()


class Item(models.Model):
    embedding = ArrayField(RealField(), size=3, null=True)

    class Meta:
        app_label = 'myapp'
        indexes = [
            HnswIndex(
                name='hnsw_idx',
                fields=['embedding'],
                m=16,
                ef=64,
                ef_construction=64,
                dim=3,
                opclasses=['dist_l2sq_ops']
            )
        ]


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        LanternExtension(),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('embedding', ArrayField(RealField(), size=3, null=True)),
            ],
        ),
        migrations.AddIndex(
            model_name='item',
            index=HnswIndex(
                fields=['embedding'],
                m=16,
                ef=64,
                ef_construction=64,
                dim=3,
                name='hnsw_idx',
                opclasses=['dist_l2sq_ops']
            ),
        )
    ]


migration = Migration('initial', 'myapp')
loader = MigrationLoader(connection, replace_migrations=False)
loader.graph.add_node(('myapp', migration.name), migration)
sql_statements = loader.collect_sql([(migration, False)])

with connection.cursor() as cursor:
    cursor.execute("DROP TABLE IF EXISTS myapp_item")
    cursor.execute('\n'.join(sql_statements))


def create_items():
    vectors = [
        [1, 1, 1],
        [2, 2, 2],
        [1, 1, 2]
    ]
    for i, v in enumerate(vectors):
        item = Item(id=i + 1, embedding=v)
        item.save()


class TestDjango:
    def setup_method(self, test_method):
        Item.objects.all().delete()

    def test_works(self):
        item = Item(id=1, embedding=[1, 2, 3])
        item.save()
        item = Item.objects.get(pk=1)
        assert item.id == 1
        assert np.array_equal(np.array(item.embedding), np.array([1, 2, 3]))

    def test_l2_distance(self):
        create_items()
        distance = L2Distance('embedding', [1, 1, 1])
        items = Item.objects.annotate(distance=distance).order_by(distance)
        assert [v.id for v in items] == [1, 3, 2]
        # assert [v.distance for v in items] == [0, 1, sqrt(3)]
        assert [v.distance for v in items] == [0, 1, 3] # TODO: Remove this and uncomment above use Euclidean distance instead of squared Euclidean distance

    def test_cosine_distance(self):
        create_items()
        distance = CosineDistance('embedding', [1, 1, 1])
        items = Item.objects.annotate(distance=distance).order_by(distance)
        assert [v.id for v in items] == [1, 2, 3]
        # assert [v.distance for v in items] == [0, 0, 0.05719095841793653]
        assert [v.distance for v in items] == [0, 0, 0.057191014] # TODO: Remove this and uncomment above when double precision supported

    def test_filter(self):
        create_items()
        distance = L2Distance('embedding', [1, 1, 1])
        items = Item.objects.alias(distance=distance).filter(distance__lt=1)
        assert [v.id for v in items] == [1]

    # TODO: Uncomment this once we support double precision
    # def test_avg(self):
    #     avg = Item.objects.aggregate(Avg('embedding'))['embedding__avg']
    #     assert avg is None
    #     Item(embedding=[1, 2, 3]).save()
    #     Item(embedding=[4, 5, 6]).save()
    #     avg = Item.objects.aggregate(Avg('embedding'))['embedding__avg']
    #     assert np.array_equal(avg, np.array([2.5, 3.5, 4.5]))

    # TODO: Uncomment this once we support double precision
    # def test_sum(self):
    #     sum = Item.objects.aggregate(Sum('embedding'))['embedding__sum']
    #     assert sum is None
    #     Item(embedding=[1, 2, 3]).save()
    #     Item(embedding=[4, 5, 6]).save()
    #     sum = Item.objects.aggregate(Sum('embedding'))['embedding__sum']
    #     assert np.array_equal(sum, np.array([5, 7, 9]))

    def test_serialization(self):
        create_items()
        items = Item.objects.all()
        for format in ['json', 'xml']:
            data = serializers.serialize(format, items)
            with mock.patch('django.core.serializers.python.apps.get_model') as get_model:
                get_model.return_value = Item
                for obj in serializers.deserialize(format, data):
                    obj.save()

    def test_clean(self):
        item = Item(id=1, embedding=[1, 2, 3])
        item.full_clean()

    def test_get_or_create(self):
        Item.objects.get_or_create(embedding=[1, 2, 3])

    def test_missing(self):
        Item().save()
        assert Item.objects.first().embedding is None