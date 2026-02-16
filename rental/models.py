from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('role', 'superadmin')
        return self.create_user(phone_number, password, **extra_fields)

class User(AbstractBaseUser):
    ROLE_CHOICES = [
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('owner', 'Owner'),
        ('renter', 'Renter'),
    ]
    
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20, unique=True)
    birthdate = models.DateField(null=True, blank=True)
    email = models.EmailField(max_length=254, unique=True, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='renter')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    @property
    def is_staff(self):
        return self.role in ['admin', 'superadmin']

    @property
    def is_superuser(self):
        return self.role == 'superadmin'

    @property
    def is_active(self):
        # You can add logic here if you want to suspend users by changing their role
        # or just return True if all users with a role are active.
        return True

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"

class Car(models.Model):
    CATEGORY_CHOICES = [
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('hatchback', 'Hatchback'),
        ('truck', 'Truck'),
        ('van', 'Van'),
    ]
    GEARBOX_CHOICES = [
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
    ]
    FUEL_CHOICES = [
        ('gasoline', 'Gasoline'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
    ]
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('suspended', 'Suspended'),
        ('unavailable', 'Unavailable'),
    ]

    car_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cars')
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    production_year = models.IntegerField()
    color = models.CharField(max_length=20, null=True, blank=True)
    seats = models.IntegerField(null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, null=True, blank=True)
    only_with_driver = models.BooleanField(default=False)
    with_driver = models.BooleanField(default=True)
    gearbox = models.CharField(max_length=10, choices=GEARBOX_CHOICES, null=True, blank=True)
    fuel = models.CharField(max_length=10, choices=FUEL_CHOICES, null=True, blank=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    max_days = models.PositiveIntegerField(default=7)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='available')
    country = models.TextField(null=True, blank=True)
    province = models.TextField(null=True, blank=True)
    city = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image_path = models.ImageField(upload_to='car_images/', null=True, blank=True)

    class Meta:
        db_table = 'cars'

    def __str__(self):
        return f"{self.brand} {self.model} ({self.production_year})"

class Rent(models.Model):
    STATUS_CHOICES = [
        ('pending payment', 'Pending Payment'),
        ('on your rent', 'On Your Rent'),
        ('not yet', 'Not Yet'),
        ('over', 'Over'),
    ]

    rent_id = models.AutoField(primary_key=True)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='rents')
    renter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rentals')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending payment')
    total_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'rents'

class Payment(models.Model):
    METHOD_CHOICES = [
        ('online', 'Online'),
        ('cash', 'Cash'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
    ]

    payment_id = models.AutoField(primary_key=True)
    rent = models.OneToOneField(Rent, on_delete=models.CASCADE, related_name='payment')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    datetime = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, null=True, blank=True)
    tracking_code = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')

    class Meta:
        db_table = 'payments'

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    comment = models.TextField()

    class Meta:
        db_table = 'reviews'


class Score(models.Model):
    score_id = models.AutoField(primary_key=True)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='scores')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scores')
    score = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        db_table = 'scores'

class Login(models.Model):
    login_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logins')
    is_signup = models.BooleanField()
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'logins'
