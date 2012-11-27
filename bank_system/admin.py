from django.contrib import admin
from models import *


admin.site.register(BankAccountDecorator)
admin.site.register(CreditAnalystDecorator)
admin.site.register(EmployeeDecorator)
admin.site.register(AttendantDecorator)
admin.site.register(ContactDecorator)
#admin.site.register(ClientDecorator)