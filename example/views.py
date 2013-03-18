from django.shortcuts import render_to_response
import sqlalchemy, sqlalchemy.orm
from sqlalchemy_models import Base, Person
from amodelform.amodelform import AModelForm
from django.forms import ModelForm
from example.models import Person as DjangoPerson
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render

engine = sqlalchemy.create_engine('sqlite:///a_storage.db')
Session = sqlalchemy.orm.sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)


class DjangoModelForm(ModelForm):
    class Meta:
        model = DjangoPerson


class SQLAlchemyModelForm(AModelForm):
    class Meta:
        model = Person


def is_empty():
    return len(session.query(Person).all()) <= 0


def show_form(request):
    engine = request.GET.get('engine', 'sqlalchemy')
    pk = request.GET.get('pk', None)
    form = None

    if engine == 'django':
        if pk is not None:
            person = DjangoPerson.objects.get(pk=pk)
            form = DjangoModelForm(instance=person)
        else:
            form = DjangoModelForm()

    elif engine == 'sqlalchemy':
        if pk is not None:
            person = session.query(Person).get(pk)
            form = SQLAlchemyModelForm(instance=person)
        else:
            form = SQLAlchemyModelForm()

    if form is not None:
        return render(request, 'form.html', {'form': form, 'engine': engine})
    else:
        return HttpResponse('Something went wrong.')


def insert(request, engine):
    if request.POST:  # submitted data
        if engine == 'sqlalchemy':
            form = SQLAlchemyModelForm(request.POST or None)
        elif engine == 'django':
            form = DjangoModelForm(request.POST or None)
        else:
            return HttpResponse('Something went wrong 2.')

        if form.is_valid():
            form.save()
            return HttpResponse('tutto ok!')
        else:
            return render(request, 'form.html',
                          {'form': form, 'engine': engine})
    else:
        engine = request.GET.get('engine', 'sqlalchemy')
        pk = request.GET.get('pk', None)
        form = None

        if engine == 'django':
            if pk is not None:
                person = DjangoPerson.objects.get(pk=pk)
                form = DjangoModelForm(instance=person)
            else:
                form = DjangoModelForm()

        elif engine == 'sqlalchemy':
            if pk is not None:
                person = session.query(Person).get(pk)
                form = SQLAlchemyModelForm(instance=person)
            else:
                form = SQLAlchemyModelForm()

        if form is not None:
            return render(request, 'form.html',
                          {'form': form, 'engine': engine})
        else:
            return HttpResponse('Something went wrong.')
