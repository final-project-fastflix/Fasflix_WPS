from django.urls import path
from .api_views import *

app_name = 'movie'

urlpatterns = [
    path('', HomePage.as_view(), name='home_page'),
    path('all/', MovieList.as_view(), name='movie_all_list'),
    path('create/', MovieCerate.as_view(), name='create'),
    path('genre/list/', GenreList.as_view(), name='genre_list'),
    path('genre/<str:kind>/list/', ListByMovieGenre.as_view(), name='genre_kind_list'),
    path('<int:sub_user_id>/list/', MarkedList.as_view(), name="preference_list"),
    path('<int:pk>/<int:sub_user_id>/', MovieDetail.as_view(), name='movie_detail'),
    path('followup/<int:sub_user_id>/', FollowUpMovies.as_view(), name='follow_up_movies'),
    # path('save_data/', save_data1,),
]