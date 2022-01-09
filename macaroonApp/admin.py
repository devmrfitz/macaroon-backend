from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Profile, CustomGroup, Transaction, FinalPayment


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'First_Name', 'Last_Name', 'user', 'public_key')


class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'description')


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('sender', 'intermediary', 'amount')


class FinalPaymentAdmin(admin.ModelAdmin):
    list_display = ('moneySender', 'moneyReceiver', 'amount')


admin.site.register(User, UserAdmin)
admin.site.register(FinalPayment, FinalPaymentAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(CustomGroup, CustomGroupAdmin)
