from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, LoginForm, CarForm, RentRequestForm
from .models import User, Car, Rent, Review, Score, Login, Payment
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Q, Sum, F
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from datetime import timedelta


def normalize_rent_datetimes(rent):
    changed = False
    if timezone.is_naive(rent.start_datetime):
        rent.start_datetime = timezone.make_aware(
            rent.start_datetime,
            timezone.get_current_timezone(),
        )
        changed = True
    if timezone.is_naive(rent.end_datetime):
        rent.end_datetime = timezone.make_aware(
            rent.end_datetime,
            timezone.get_current_timezone(),
        )
        changed = True
    return changed


def update_rent_status_with_time(rent, now=None, include_pending=False):
    if rent.status == 'pending payment' and not include_pending:
        return
    if now is None:
        now = timezone.now()

    normalize_rent_datetimes(rent)
    start = rent.start_datetime
    end = rent.end_datetime

    if now < start:
        new_status = 'not yet'
    elif start <= now <= end:
        new_status = 'on your rent'
    else:
        new_status = 'over'

    if rent.status != new_status:
        rent.status = new_status
    rent.save(update_fields=['status', 'start_datetime', 'end_datetime'])

def home(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    fuel = request.GET.get('fuel', '')
    gearbox = request.GET.get('gearbox', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    cars = Car.objects.filter(status='available')

    if query:
        cars = cars.filter(
            Q(brand__icontains=query) | 
            Q(model__icontains=query) | 
            Q(description__icontains=query)
        )
    if category:
        cars = cars.filter(category=category)
    if fuel:
        cars = cars.filter(fuel=fuel)
    if gearbox:
        cars = cars.filter(gearbox=gearbox)
    if min_price:
        cars = cars.filter(fee__gte=min_price)
    if max_price:
        cars = cars.filter(fee__lte=max_price)

    categories = Car.objects.values_list('category', flat=True).distinct()
    fuels = Car.objects.values_list('fuel', flat=True).distinct()
    gearboxes = Car.objects.values_list('gearbox', flat=True).distinct()

    return render(request, 'rental/home.html', {
        'cars': cars,
        'categories': categories,
        'fuels': fuels,
        'gearboxes': gearboxes,
        'filters': request.GET
    })

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Login.objects.create(user=user, is_signup=True)
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'rental/signup.html', {'form': form})

def signin_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier'].strip()
            password = form.cleaned_data['password']

            phone_number = identifier
            if '@' in identifier:
                matched_user = User.objects.filter(email__iexact=identifier).first()
                phone_number = matched_user.phone_number if matched_user else None

            user = None
            if phone_number:
                user = authenticate(
                    request,
                    phone_number=phone_number,
                    password=password
                )
            if user:
                login(request, user)
                Login.objects.create(user=user, is_signup=False)
                messages.success(request, f"Welcome back, {user.first_name}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid email/phone number or password.")
    else:
        form = LoginForm()
    return render(request, 'rental/signin.html', {'form': form})

def signout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    user = request.user
    section = request.GET.get('section', 'profile')
    context = {'user': user, 'section': section}
    
    # Handle car addition directly in dashboard
    if request.method == 'POST' and section == 'cars':
        car_form = CarForm(request.POST, request.FILES)
        if car_form.is_valid():
            car = car_form.save(commit=False)
            car.owner = user
            car.save()
            if user.role == 'renter':
                user.role = 'owner'
                user.save()
                messages.success(request, "Car added successfully. You are now an Owner!")
            else:
                messages.success(request, "Car added successfully.")
            return redirect('/dashboard/?section=cars')
        else:
            context['car_form'] = car_form
            # Ensure the form is open on reload if there are errors
            context['show_car_form'] = True 
    
    # Renter & Owner common sections
    if section == 'profile':
        pass # User info already in context
    elif section == 'rents':
        # Everyone sees their personal rentals here
        rents = Rent.objects.filter(renter=user).order_by('-start_datetime')
        now = timezone.now()
        for rent in rents:
            update_rent_status_with_time(rent, now)
        context['my_rents'] = rents
    elif section == 'cars':
        if user.role in ['owner', 'admin', 'superadmin']:
            context['my_cars'] = Car.objects.filter(owner=user).order_by('-car_id')
            context['category_choices'] = Car.CATEGORY_CHOICES
            context['gearbox_choices'] = Car.GEARBOX_CHOICES
            context['fuel_choices'] = Car.FUEL_CHOICES
        if 'car_form' not in context:
            context['car_form'] = CarForm()
    elif section == 'car_history':
        if user.role in ['owner', 'superadmin']:
            # Owner/superadmin history for their own cars only.
            rents = Rent.objects.filter(car__owner=user).order_by('-start_datetime')
            now = timezone.now()
            for rent in rents:
                update_rent_status_with_time(rent, now)
            context['my_cars_rents'] = rents

    # Admin common sections
    if user.role in ['admin', 'superadmin']:
        if section == 'suspend':
            context['all_users'] = User.objects.all()
            context['all_cars'] = Car.objects.all()
        elif section == 'reports':
            context['all_rents'] = Rent.objects.all()
            context['all_cars'] = Car.objects.all()
            context['all_users'] = User.objects.all()
        elif section == 'manage_admins' and user.role == 'superadmin':
            context['admins'] = User.objects.filter(role='admin')
        elif section == 'rents': # Admins see all rents
            context['all_rents'] = Rent.objects.all()

    return render(request, 'rental/dashboard.html', context)

def car_detail(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    reviews = car.reviews.select_related('user').all().order_by('-review_id')
    paid_renter_ids = set(
        Payment.objects.filter(
            status='successful',
            rent__car=car
        ).values_list('rent__renter_id', flat=True)
    )
    score_map = {}
    for uid, score_value in Score.objects.filter(car=car).order_by('-score_id').values_list('user_id', 'score'):
        score_map.setdefault(uid, score_value)

    eligible_score_count = 0
    used_score_count = 0
    can_score = False
    if request.user.is_authenticated:
        eligible_score_count = Payment.objects.filter(
            status='successful',
            rent__car=car,
            rent__renter=request.user,
            rent__status='over',
        ).count()
        used_score_count = Score.objects.filter(
            car=car,
            user=request.user,
        ).count()
        can_score = eligible_score_count > used_score_count

    today = timezone.localdate()
    max_start_date = today + timedelta(days=30)
    week_start_offset = (today.weekday() + 1) % 7  # Sunday=0
    calendar_start = today - timedelta(days=week_start_offset)
    max_start_weekday = (max_start_date.weekday() + 1) % 7
    calendar_end = max_start_date + timedelta(days=(6 - max_start_weekday))

    blocked_rents = car.rents.filter(status__in=['pending payment', 'not yet', 'on your rent'])
    blocked_iso_dates = set()
    for rent in blocked_rents:
        normalize_rent_datetimes(rent)
        start_date = timezone.localtime(rent.start_datetime).date()
        end_date = timezone.localtime(rent.end_datetime).date()
        overlap_start = max(start_date, calendar_start)
        overlap_end = min(end_date, calendar_end)
        if overlap_start <= overlap_end:
            current_day = overlap_start
            while current_day <= overlap_end:
                blocked_iso_dates.add(current_day.isoformat())
                current_day += timedelta(days=1)

    rent_form = RentRequestForm()
    return render(request, 'rental/car_detail.html', {
        'car': car, 
        'reviews': reviews,
        'rent_form': rent_form,
        'can_score': can_score,
        'paid_renter_ids': paid_renter_ids,
        'calendar_start': calendar_start.isoformat(),
        'calendar_end': calendar_end.isoformat(),
        'today_date': today.isoformat(),
        'max_start_date': max_start_date.isoformat(),
        'max_days': car.max_days,
        'blocked_iso_dates': sorted(blocked_iso_dates),
    })

@login_required
def add_car(request):
    # Any logged in user can add a car
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.owner = request.user
            car.save()
            
            # If a renter adds a car, they become an owner
            if request.user.role == 'renter':
                request.user.role = 'owner'
                request.user.save()
                messages.success(request, "Car added successfully. You are now an Owner!")
            else:
                messages.success(request, "Car added successfully.")
            return redirect('/dashboard/?section=cars')
    else:
        form = CarForm()
    return render(request, 'rental/add_car.html', {'form': form})

@login_required
def edit_car(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    if car.owner != request.user and request.user.role not in ['admin', 'superadmin']:
        messages.error(request, "Unauthorized.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, "Car details updated successfully.")
            return redirect('/dashboard/?section=cars')
        messages.error(request, "Could not update car. Please check the entered values.")
        return redirect('/dashboard/?section=cars')

    return redirect('/dashboard/?section=cars')

@login_required
def request_rent(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    if request.user == car.owner:
        messages.error(request, "You cant rent your own car.")
        return redirect('car_detail', car_id=car_id)

    if request.method == 'POST':
        form = RentRequestForm(request.POST)
        if form.is_valid():
            rent = form.save(commit=False)
            # HTML datetime-local input can produce naive datetimes; convert to aware.
            normalize_rent_datetimes(rent)

            if rent.end_datetime <= rent.start_datetime:
                messages.error(request, "End date/time must be after start date/time.")
                return redirect('car_detail', car_id=car_id)

            start_date = timezone.localtime(rent.start_datetime).date()
            end_date = timezone.localtime(rent.end_datetime).date()
            today = timezone.localdate()
            latest_start = today + timedelta(days=30)

            if start_date < today or start_date > latest_start:
                messages.error(request, "Start date must be between today and 30 days from now.")
                return redirect('car_detail', car_id=car_id)

            duration_days = (end_date - start_date).days + 1
            if duration_days > car.max_days:
                messages.error(request, f"Maximum reservation duration for this car is {car.max_days} day(s).")
                return redirect('car_detail', car_id=car_id)

            overlaps_existing = car.rents.filter(
                status__in=['pending payment', 'not yet', 'on your rent'],
                start_datetime__lte=rent.end_datetime,
                end_datetime__gte=rent.start_datetime,
            ).exists()
            if overlaps_existing:
                messages.error(request, "Selected range includes unavailable dates.")
                return redirect('car_detail', car_id=car_id)

            rent.car = car
            rent.renter = request.user
            rent.total_fee = (car.fee * Decimal(duration_days)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            rent.save()
            messages.success(request, "Rent request submitted.")
            return redirect('/dashboard/?section=rents')
    return redirect('car_detail', car_id=car_id)

@login_required
def add_review(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    if request.method == 'POST':
        comment = request.POST.get('comment', '').strip()
        if not comment:
            messages.error(request, "Please write a comment before submitting.")
            return redirect('car_detail', car_id=car_id)

        Review.objects.create(
            car=car,
            user=request.user,
            comment=comment,
        )
        messages.success(request, "Comment submitted.")
    return redirect('car_detail', car_id=car_id)


@login_required
def add_score(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    if request.method != 'POST':
        return redirect('car_detail', car_id=car_id)

    eligible_score_count = Payment.objects.filter(
        status='successful',
        rent__car=car,
        rent__renter=request.user,
        rent__status='over',
    ).count()

    used_score_count = Score.objects.filter(
        car=car,
        user=request.user
    ).count()

    if eligible_score_count <= used_score_count:
        messages.error(request, "Score section opens for completed paid rents.")
        return redirect('car_detail', car_id=car_id)

    raw_score = request.POST.get('score')
    if raw_score not in ['1', '2', '3', '4', '5']:
        messages.error(request, "Please select a valid star rating.")
        return redirect('car_detail', car_id=car_id)

    try:
        Score.objects.create(
            car=car,
            user=request.user,
            score=int(raw_score),
        )
    except IntegrityError:
        messages.error(request, "Scoring is blocked by current database constraints. Please update the scores table constraint.")
        return redirect('car_detail', car_id=car_id)

    messages.success(request, "Score submitted.")
    return redirect('car_detail', car_id=car_id)

@login_required
def admin_action(request, action, target_type, target_id):
    if request.user.role not in ['admin', 'superadmin']:
        messages.error(request, "Unauthorized.")
        return redirect('dashboard')
    
    if target_type == 'user':
        target = get_object_or_404(User, pk=target_id)
        if action == 'suspend':
            # Instead of is_active column, we could change role to a 'suspended' role 
            # or handle it via a different logic. Since we can't add columns, 
            # let's assume 'suspended' is not a role in db_schema.sql but we can 
            # maybe just prevent login or similar. 
            # For now, I'll just show a message since we don't have a status column.
            messages.info(request, f"Suspension for {target.phone_number} requires a status column.")
        elif action == 'make_admin' and request.user.role == 'superadmin':
            target.role = 'admin'
            target.save()
            messages.success(request, f"User {target.phone_number} is now an admin.")
    
    elif target_type == 'car':
        target = get_object_or_404(Car, pk=target_id)
        if action == 'suspend':
            target.status = 'suspended' if target.status != 'suspended' else 'available'
            target.save()
            messages.success(request, f"Car {target.brand} {target.model} status updated.")

    return redirect('/dashboard/?section=suspend')

@login_required
def car_management(request, car_id, action):
    car = get_object_or_404(Car, pk=car_id)
    if car.owner != request.user and request.user.role not in ['admin', 'superadmin']:
        messages.error(request, "Unauthorized.")
        return redirect('dashboard')

    if action not in ['deactivate', 'activate', 'remove']:
        messages.error(request, "Invalid action.")
        return redirect('/dashboard/?section=cars')

    if action == 'deactivate':
        if car.status == 'suspended':
            messages.error(request, "Suspended cars can only be managed by admin.")
            return redirect('/dashboard/?section=cars')
        if car.status == 'unavailable':
            messages.info(request, f"Car {car.brand} {car.model} is already deactivated.")
            return redirect('/dashboard/?section=cars')
        car.status = 'unavailable'
        car.save(update_fields=['status'])
        messages.info(request, f"Car {car.brand} {car.model} deactivated.")
    elif action == 'activate':
        if car.status == 'suspended' and request.user.role not in ['admin', 'superadmin']:
            messages.error(request, "This car is suspended by admin and cannot be activated by owner.")
            return redirect('/dashboard/?section=cars')
        car.status = 'available'
        car.save()
        messages.success(request, f"Car {car.brand} {car.model} activated.")
    elif action == 'remove':
        # Check if there are active rents before deleting
        if car.rents.filter(status__in=['pending payment', 'on your rent', 'not yet']).exists():
            messages.error(request, "Cannot delete car with active or pending rent requests.")
        else:
            car.delete()
            messages.warning(request, f"Car removed successfully.")
            
    return redirect('/dashboard/?section=cars')

@login_required
def reports(request):
    if request.user.role not in ['admin', 'superadmin']:
        return redirect('dashboard')
    
    context = {
        'total_users': User.objects.count(),
        'total_cars': Car.objects.count(),
        'total_rents': Rent.objects.count(),
        'total_revenue': Payment.objects.filter(status='successful').aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'recent_logins': Login.objects.order_by('-datetime')[:10]
    }
    return render(request, 'rental/reports.html', context)

@login_required
def rent_action(request, rent_id, action):
    rent = get_object_or_404(Rent, pk=rent_id)
    now = timezone.now()
    
    # Check permissions
    if action == 'pay':
        if rent.renter != request.user:
            messages.error(request, "Unauthorized.")
            return redirect('dashboard')
            
        # Determine status based on exact date+time boundaries.
        update_rent_status_with_time(rent, now, include_pending=True)
        # Create a successful payment record
        Payment.objects.create(
            rent=rent,
            total_amount=rent.total_fee,
            method='online',
            status='successful'
        )
        # Credit the owner account balance when payment is completed.
        User.objects.filter(pk=rent.car.owner_id).update(balance=F('balance') + rent.total_fee)
        messages.success(request, f"Payment successful! Status: {rent.get_status_display()}")
        return redirect('/dashboard/?section=rents')
        
    elif action == 'cancel':
        if rent.renter != request.user and rent.car.owner != request.user:
            messages.error(request, "Unauthorized.")
            return redirect('dashboard')
        # Logic for cancellation
        rent.status = 'over' # Or maybe add a 'cancelled' status to models if possible
        rent.save()
        messages.info(request, "Rent request cancelled.")
        return redirect('/dashboard/?section=rents')
        
    return redirect('dashboard')
