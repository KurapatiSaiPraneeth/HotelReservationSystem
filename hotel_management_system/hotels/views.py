from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.views.generic import ListView, FormView, View
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from pytz import timezone as pytimezone
import datetime
import ast
from decimal import Decimal
from .models import Hotel, Room, Reservation
from .forms import AvailabilityForm
from .booking_functions.availability import check_availability

# Create your views here.

current_time = timezone.now()
tz = pytimezone('America/Chicago')
current_time = current_time.astimezone(tz)

@login_required(login_url='guests:login')
def room_list(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)

    rooms = Room.objects.filter(hotel=hotel, available_to__gte=current_time.date())
    context = {'hotel': hotel, 'rooms': rooms}
    room_list = {}

    for room in rooms:
        room_list[room.id] = {}
        room_list[room.id]["category"] = room.category
        room_list[room.id]["price"] = room.price
        room_list[room.id]["photo"] = room.photo
        room_list[room.id]["description"] = room.description
        room_detail_url = reverse('hotels:room_detail', kwargs={'room_id': room.id})
        room_list[room.id]["room_detail_url"] = room_detail_url

    if not room_list:
        messages.warning(request, 'No rooms are available at this moment !!!')
    context = {
        "room_list": room_list
    }
    return render(request, 'hotels/room_list_view.html', context)

@login_required(login_url='guests:login')
def room_detail(request, room_id):
    room_record = Room.objects.get(id=room_id)
    room_detail_dict = {
        "room_reservation": {},
        }
    room_type = room_record.category
    room_detail_dict["room_reservation"]["room_type"] = room_type
    room_detail_url = reverse('hotels:room_detail', kwargs={'room_id': room_id})
    room_detail_dict["room_reservation"]["room_detail_url"] = room_detail_url

    context = {"room_detail_dict": room_detail_dict}

    if request.method=='POST':
        check_in_date = request.POST.get("checkin_date")
        checkin_date = datetime.datetime.strptime(check_in_date, '%Y-%m-%d').date()
        check_out_date = request.POST.get("checkout_date")
        checkout_date = datetime.datetime.strptime(check_out_date, '%Y-%m-%d').date()
        no_of_guests = request.POST.get("no_of_guests")
        no_of_rooms = request.POST.get("no_of_rooms")

        room_detail_dict["room_reservation"]["checkin_date"] = check_in_date
        room_detail_dict["room_reservation"]["checkout_date"] = check_out_date
        room_detail_dict["room_reservation"]["no_of_guests"] = no_of_guests
        room_detail_dict["room_reservation"]["no_of_rooms"] = no_of_rooms

        room_availability_price = check_room_availability(
            request, room_record, checkin_date, checkout_date, no_of_guests, no_of_rooms
            )
        if room_availability_price:
            room_detail_dict["room_reservation"]["payment_details"] = room_availability_price
            room_reservation_url = reverse('hotels:room_reservation', kwargs={'room_id': room_id})
            room_detail_dict["room_reservation"]["reservation_url"] = room_reservation_url

    return render(request, 'hotels/room_detail_view.html', context)


def check_room_availability(request, room_record, guest_checkin, guest_checkout, no_of_guests, no_of_rooms):
    if guest_checkout <= guest_checkin:
        messages.warning(request, 'Checkout date must be after checkin date !!!')
        return False
    if guest_checkin <= current_time.date():
        messages.warning(request, 'Checkin date must be at least one day from today !!!')
        return False

    allowed_guests = int(room_record.capacity) * int(no_of_rooms)
    if int(no_of_guests) > allowed_guests:
        messages.warning(request, f'Only {room_record.capacity} guests allowed for {room_record.category} room type !!! ')
        return False

    total_nights = (guest_checkout - guest_checkin).days
    return room_record.price * total_nights * int(no_of_rooms)


@login_required(login_url='guests:login')
def room_reservation(request, room_id, **kwargs):
    if request.method == "POST":
        reservation_list = []
        room_details = request.POST.get("room_details")
        room_details = room_details.replace("Decimal('", "").replace("')", "")

        # Converting the cleaned string to a dictionary using ast.literal_eval()
        room_details = ast.literal_eval(room_details)
        check_in_date = room_details.get("checkin_date")
        checkin_date = datetime.datetime.strptime(check_in_date, '%Y-%m-%d').date()
        check_out_date = room_details.get("checkout_date")
        checkout_date = datetime.datetime.strptime(check_out_date, '%Y-%m-%d').date()
        no_of_guests = room_details.get("no_of_guests")
        no_of_rooms = room_details.get("no_of_rooms")
        total_price = room_details.get("payment_details")

        for room in range(int(no_of_rooms)):
            reservation_instance = Reservation(
                    user = request.user,
                    room = Room.objects.get(id=room_id),
                    check_in = checkin_date,
                    check_out = checkout_date,
                    adults = no_of_guests,
                    total_price = total_price
            )
            reservation_instance.save()

        messages.success(request, 'Your payment has been received. Your reservation is confirmed.')
    return redirect('hotels:reservation_history')


@login_required(login_url='guests:login')
def reservation_history(request):
    user_obj = request.user

    history = []

    user_reservations = Reservation.objects.filter(
        user=user_obj
        ).values('room','check_in','check_out','adults', 'total_price').annotate(no_of_rooms=Count('room'))

    for reservation in user_reservations:
        r = {}

        room_obj = Room.objects.get(id=int(reservation.get("room")))
        r["Hotel"] = f'{room_obj.hotel}-{room_obj.category}'
        r["checkin"] = reservation.get("check_in")
        r["qdisabled"] = "qdisabled" if r["checkin"] <= current_time.date() else ""
        print("***", r["checkin"], current_time.date())
        r["checkout"] = reservation.get("check_out")
        r["guests"] = reservation.get("adults")
        r["rooms"] = reservation.get("no_of_rooms")
        cancle_reservation_url = reverse('hotels:cancle_reservation', kwargs={"room_id": room_obj.id, "checkin":r["checkin"].strftime('%Y-%m-%d'), "checkout":r["checkout"].strftime('%Y-%m-%d')})
        r["cancle_reservation_url"] = cancle_reservation_url
        history.append(r)

    context = {"reservations": history}
    return render(request, 'hotels/reservation_list.html', context)


@login_required(login_url='guests:login')
def cancle_reservation(request, room_id, checkin, checkout):
    user_obj = request.user
    Reservation.objects.filter(
            user=user_obj,
            check_in = checkin,
            check_out = checkout
            ).delete()
    messages.success(request, 'Your reservation has been cancelled.')
    return redirect('hotels:reservation_history')


