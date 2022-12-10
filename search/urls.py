from django.urls import include, path
from . import views


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('search/<str:query>/', views.get_results, name='get_results'),
    path('doc/<str:doc_id>/', views.get_content, name='get_content'),
]
