from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import Equipment,Booking
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def home(request):
    # Retrieve all equipment data
    user = request.user    
    all_equipment = Equipment.objects.all()
    bookings = None
    # Filter equipment based on search query
    query = request.GET.get('q')
    if query:
        all_equipment = all_equipment.filter(DeviceName__icontains=query)

    sort_by = request.GET.get('sort_by')
    if sort_by == 'name_az':
        all_equipment = all_equipment.order_by('DeviceName')
    elif sort_by == 'type':
        all_equipment = all_equipment.order_by('DeviceTypeID')  # Replace 'name' with the actual field name of equipment type
     # Replace 'return_date' with the actual field name of return date
    elif sort_by == 'Availability':
        all_equipment = all_equipment.order_by('Availability')  # Replace 'return_date' with the actual field name of return date
    elif sort_by == 'return_date':
        bookings = Booking.objects.filter(user = user)
        bookings = bookings.order_by('return_date')  # Replace 'return_date' with the actual field name of return date
    return render(request, 'home.html', {'all_equipment': all_equipment, 'bookings':bookings ,'user':user})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Optionally, log in the user after registration
            # login(request, user)
            messages.success(request,"your account has been created you can login after admin approval!")  # Redirect to home page after successful registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    if user.ApprovalStatus:  # Check if user is approved by admin
                        login(request, user)
                        return redirect('home')
                    else:
                        messages.error(request, 'Your account is not approved by the admin yet.')
                else:
                    messages.error(request, 'Your account is disabled.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required(login_url='login')
def booking_page(request,equipment_id):
    equipment = Equipment.objects.get(pk=equipment_id)    
    return render(request, "booking_page.html",{'equipment':equipment})

@login_required(login_url='login')
def initiate_reservation(request,equipment_id):
    equipment = get_object_or_404(Equipment, pk=equipment_id)
    if request.method == 'POST':
        booking_date = request.POST.get('booking_date')
        return_date = request.POST.get('return_date')
        my_booking = Booking(user = request.user,return_date=return_date, equipment=equipment, booking_date=booking_date)
        my_booking.save()
        messages.success(request, 'reservation added by hasnat for my device')
    
    return redirect('user_profile')
@login_required(login_url='login')
def user_profile(request):
    user = request.user
    my_booking = Booking.objects.filter(user = user)
    return render(request ,"profile.html", {'user':user,'booking':my_booking})

@login_required(login_url='login')
def cancel_reservation(request,pk):
    user = request.user
    my_booking = Booking.objects.get(pk = pk)
    my_booking.delete()
    return redirect('user_profile')
