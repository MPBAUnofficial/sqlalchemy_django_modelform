from django.conf.urls import patterns, include, url
from example.views import show_form, insert

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'sqlalchemy_modelform.views.home', name='home'),
    # url(r'^sqlalchemy_modelform/', include('sqlalchemy_modelform.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^form/', show_form),
    url(r'^insert/([a-z]+)', insert)
)
