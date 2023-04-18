from django.db import models
from django.conf import settings
# Create your models here.

class Hotel(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='hotels/', blank=True)

    def __str__(self):
        return self.name

class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    category = models.CharField(max_length=100)
    beds = models.IntegerField()
    capacity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available_from = models.DateField()
    available_to = models.DateField()
    total_rooms = models.PositiveIntegerField()
    photo = models.ImageField(upload_to='rooms/', blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f'{self.hotel} -  {self.category}'

class Reservation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reservations')
    check_in = models.DateField()
    check_out = models.DateField()
    adults = models.PositiveIntegerField()
    children = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f'{self.user.username} - {self.room}'



"""

class Reservation(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reservations')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    checkin = models.DateField()
    checkout = models.DateField()
    adults = models.PositiveIntegerField()
    children = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} - {self.room}'

    def clean(self):
        if self.checkout <= self.checkin:
            raise ValidationError('Checkout date must be after checkin date')

        if timezone.now().date() >= self.checkin:
            raise ValidationError('Checkin date must be in the future')

        if self.checkin <= timezone.now().date() + timezone.timedelta(days=1):
            raise ValidationError('Checkin date must be at least one day from today')

    def cancel_reservation(self):
        cancel_date = self.checkin - timezone.timedelta(days=1)
        if timezone.now().date() >= cancel_date:
            raise ValidationError('Cannot cancel reservation less than 24 hours before checkin')

        self.delete()

    @property
    def total_price(self):
        nights = (self.checkout - self.checkin).days
        return self.room.price * nights

    @classmethod
    def get_user_reservations(cls, user):
        return cls.objects.filter(room__hotel__in=user.favorite_hotels.all())

    class Meta:
        ordering = ['-created_at']
 """

