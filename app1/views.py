from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm, ReservationForm
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.db import transaction
from django.db.models import Q
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
def booking_page(request, equipment_id):
    equipment = get_object_or_404(Equipment, pk=equipment_id)
    return render(request, 'booking_page.html', {'equipment': equipment, 'form': ReservationForm()})


@login_required(login_url='login')
@require_POST
def initiate_reservation(request, equipment_id):
    if not request.user.ApprovalStatus:
        return HttpResponseForbidden('Account approval is required to reserve equipment.')
    form = ReservationForm(request.POST)
    with transaction.atomic():
        equipment = get_object_or_404(Equipment.objects.select_for_update(), pk=equipment_id)
        if form.is_valid():
            start, end = form.cleaned_data['booking_date'], form.cleaned_data['return_date']
            conflicts = Booking.objects.filter(
                equipment=equipment, status__in=['Pending', 'Approved'], booking_date__lte=end,
            ).exclude(admin_approval='Rejected').filter(Q(return_date__gte=start) | Q(return_date__isnull=True))
            if not equipment.Availability:
                form.add_error(None, 'This equipment is currently unavailable.')
            elif conflicts.exists():
                form.add_error(None, 'This equipment is already reserved during those dates. Choose another date range.')
            else:
                Booking.objects.create(user=request.user, equipment=equipment, booking_date=start, return_date=end)
                messages.success(request, 'Your reservation has been submitted for approval.')
                return redirect('user_profile')
    return render(request, 'booking_page.html', {'equipment': equipment, 'form': form}, status=400)


@login_required(login_url='login')
def user_profile(request):
    bookings = Booking.objects.filter(user=request.user).select_related('equipment').order_by('-booking_date')
    return render(request, 'profile.html', {'user': request.user, 'booking': bookings})


@login_required(login_url='login')
@require_POST
def cancel_reservation(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    # Preserve the reservation history; returned bookings must not be rewritten.
    Booking.objects.filter(pk=booking.pk, status__in=['Pending', 'Approved']).update(status='Cancelled')
    return redirect('user_profile')
