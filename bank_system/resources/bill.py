from datetime import datetime
from should_dsl import should, ShouldNotSatisfied
from domain.supportive.association_error import AssociationError
from domain.supportive.rule import rule
from domain.resource.work_item import WorkItem
from domain.supportive.rule_manager import RuleManager
from bank_system.models import BankAccountDecorator
from django.contrib.auth.models import User

class Bill(WorkItem):
    ''' A Bill has an account, type, value payed, value to pay, date and time '''
    def __init__(self, account, type_, value, payment_value):
        WorkItem.__init__(self)
        self.bill_list = ['House bill', 'Eletricity bill', 'Water bill', 'Credit card bill']
        self.value = value
        self.datetime = datetime.now()
        self.payment_value = 0
        if type_ in self.bill_list:
            self.type_ = type_
        else:
            raise AssociationError('A Bill is expected , instead %s passed'%(type_))
        if not value == payment_value:
            raise AssociationError('Equal value is expected for the payment, Value payment is %s , payment value is %s' % (value,payment_value))
        if not RuleManager.get_instance().check_rule('should_be_instance_of_bank_account', account):
           raise AssociationError('Bank Account instance expected, instead %s passed' % type(account))
        self.account = account
        self.account.average_credit -= int(self.value)
        self.account.save_base()