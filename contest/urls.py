from django.urls import path
from . import views

app_name = 'contest'

urlpatterns = [
    path('', views.index, name='index'),
    path('vote/', views.vote, name='vote'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]
