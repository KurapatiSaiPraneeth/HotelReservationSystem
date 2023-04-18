from django.urls import path
from .views import room_list, room_detail, room_reservation, reservation_history
app_name = 'hotels'

urlpatterns = [
    path('<int:hotel_id>/room_list/', room_list, name='room_list'),
    path('<int:room_id>/room_detail', room_detail, name='room_detail'),
    path('<int:room_id>/room_reservation', room_reservation, name='room_reservation'),
    path('reservation_history', reservation_history, name='reservation_history'),
]