from django.contrib import admin
from .models import User, Car, Rent, Payment, Review, Score, Login

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'first_name', 'last_name', 'role', 'is_staff')
    search_fields = ('phone_number', 'first_name', 'last_name', 'email')

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'production_year', 'owner', 'status', 'fee')
    list_filter = ('status', 'category', 'fuel', 'gearbox')
    search_fields = ('brand', 'model', 'owner__phone_number')

@admin.register(Rent)
class RentAdmin(admin.ModelAdmin):
    list_display = ('car', 'renter', 'start_datetime', 'end_datetime', 'status', 'total_fee')
    list_filter = ('status',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('rent', 'total_amount', 'method', 'status', 'datetime')
    list_filter = ('status', 'method')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('car', 'user', 'comment')

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('car', 'user', 'score')
    list_filter = ('score',)

@admin.register(Login)
class LoginAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_signup', 'datetime')
