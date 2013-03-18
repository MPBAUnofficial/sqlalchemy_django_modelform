from django.forms import CharField, DateField, IntegerField, BooleanField, \
    Textarea, DecimalField, DateTimeField, ChoiceField
from django import forms
from example.sqlalchemy_models import Base
import sqlalchemy
from sqlalchemy import orm
from collections import OrderedDict

# TODO: retrieve informations from settings
engine = sqlalchemy.create_engine('sqlite:///a_storage.db')
Session = sqlalchemy.orm.sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)


def converts(*args):
    def _inner(func):
        func._converter_for = frozenset(args)
        return func

    return _inner


class ModelConverter(object):
    """
    Simply converts a sqlalchemy field into a Django Form one.
    """
    def __init__(self):
        self.converters = {}

        for name in dir(self):
            obj = getattr(self, name)
            if hasattr(obj, '_converter_for'):
                for classname in obj._converter_for:
                    self.converters[classname] = obj

    def convert(self, column):
        converter = self.converters[type(column.type).__name__]
        form_field = converter(field=column.type)
        return form_field

    @converts('String', 'Unicode')
    def string_converter(self, field):
        return CharField(max_length=field.length)

    @converts('Text', 'UnicodeText', 'types.LargeBinary', 'types.Binary')
    def text_converter(self, field):
        return CharField(widget=Textarea, max_length=field.length)

    @converts('Boolean')
    def boolean_converter(self, field):
        return BooleanField(required=False)

    @converts('Date')
    def date_converter(self, field):
        return DateField()

    @converts('DateTime')
    def datetime_converter(self, field):
        return DateTimeField()

    @converts('Enum')
    def enum_converter(self, field):
        return ChoiceField(choices=field.enums)

    @converts('Integer', 'SmallInteger')
    def integer_converter(self, field):
        unsigned = getattr(field, 'unsigned', False)
        if unsigned:
            return IntegerField(validators=[lambda x: x >= 0])
        return IntegerField()

    @converts('Numeric', 'Float')
    def decimal_converter(self, field):
        places = getattr(field, 'scale')
        return DecimalField(decimal_places=places)

    # TODO: implement missing convertions
    #
    # @converts('databases.mysql.MSYear')
    #
    # @converts('databases.postgres.PGInet', 'dialects.postgresql.base.INET')
    #
    # @converts('dialects.postgresql.base.MACADDR')
    #
    # @converts('dialects.postgresql.base.UUID')
    #
    # @converts('MANYTOONE')
    #
    # @converts('MANYTOMANY', 'ONETOMANY')
    #


def save(self, commit=True):
    if not self.is_valid():
        raise ValueError('N00B, the form is not valid!')

    data = self.cleaned_data

    if self.instance is not None:
        row = self.instance
        for field in self.changed_data:
            setattr(row, field, data[field])
    else:
        row = self.Meta.model(**data)

    if commit:
        session.add(row)
        session.commit()

    return row


class AModelForm(forms.Form):
    """
    Pseudo metaclass which generates a Django Form based on a sqlalchemy model
    (should be similar to django ModelForm).
    The generated Form will have all the fields of the provided model
    (except for the primary key, unless specified) and a 'save' method.
    """

    def __new__(cls, data=None, initial=None, instance=None, *args, **kwargs):
        if instance is None and not hasattr(cls.Meta, 'model'):
            return ValueError('ModelForm has no model class specified.')

        form_attrs = OrderedDict()
        columns = OrderedDict(cls.Meta.model.__table__.columns.items())
        model_converter = ModelConverter()

        # try to get the field list from 'Meta', otherwise all the
        # fields of the model will have the respective field in the form
        fields = list(getattr(cls.Meta, 'fields', columns.iterkeys()))

        # remove excluded fields
        for excluded_field in getattr(cls.Meta, 'exclude', ()):
            if excluded_field in fields:
                fields.remove(excluded_field)

        # generate form fields
        for field_name, sqlalchemy_field in columns.iteritems():
            # exclude primary key and fields that are not listed in 'fields'
            if (not getattr(sqlalchemy_field, 'primary_key', False)
                    or kwargs.get('show_primary_key', False)) \
                    and field_name in fields:
                form_attrs[field_name] = \
                    model_converter.convert(sqlalchemy_field)

        form_attrs['save'] = save
        form_attrs['Meta'] = cls.Meta
        form_attrs['instance'] = instance or None

        initial = initial or {}  # make sure 'initial' is a dictionary

        # set field values from instance as initial value
        # where an initial value is not provided
        if instance is not None:
            for key in cls.Meta.model.__table__.columns.keys():
                if hasattr(instance, key):  # instance model fields
                    initial.setdefault(key, getattr(instance, key))

        # generate and return the form
        new_form = type(cls.__name__, (forms.Form,), form_attrs)
        return new_form(data=data, initial=initial, *args, **kwargs)

