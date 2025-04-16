from django.urls import path
from analyzer.views import IndexView, CreatePresetView, delete_preset, results, clear_session

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('create_preset/<str:preset_type>/', CreatePresetView.as_view(), name='create_preset'),
    path('delete_preset/<int:id>/', delete_preset, name='delete_preset'),
    path('results/', results, name='results'),
    path('c/', clear_session, name='clear')
]