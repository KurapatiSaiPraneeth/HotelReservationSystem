from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .forms import LoginForm, GuestSignUpForm
from hotels.models import Hotel
from django.db.models import Min


# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = GuestSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(user.password)
            user.save()
            login(request, user)
            messages.success(request, 'Your account has been created successfully!')
            return redirect('guests:dashboard')
        return redirect('guests:login')
    else:
        form = GuestSignUpForm()
    return render(request, 'guests/signup_form.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('guests:dashboard')
    else:
        form = LoginForm()
    return render(request, 'guests/login_form.html', {'form': form})

def custom_admin_logout(request):
    logout(request)
    return redirect('guests:login')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('guests:login')

@login_required(login_url='guests:login')
def dashboard(request):
    hotels = Hotel.objects.annotate(min_room_price=Min('rooms__price'))
    hotel_list = {}
    for hotel in hotels:
        hotel_list[hotel.id] = {}
        hotel_list[hotel.id]["name"] = hotel.name
        hotel_list[hotel.id]["address"] = hotel.address
        hotel_list[hotel.id]["description"] = hotel.description
        hotel_list[hotel.id]["photo"] = hotel.photo
        rooms_url = reverse('hotels:room_list', kwargs={'hotel_id': hotel.id})
        hotel_list[hotel.id]["rooms_url"] = rooms_url
        hotel_list[hotel.id]["min_room_price"] = hotel.min_room_price
    if not hotel_list:
        messages.warning(request, 'No Hotels are available at this moment !!!')
    context = {
        "hotel_list": hotel_list
    }
    return render(request, 'hotels/hotel_list.html', context)