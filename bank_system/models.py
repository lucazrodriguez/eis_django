#coding:utf-8

import sys
sys.path.append("home/lucas/Documentos/NSI/eis/eispatterns-examples")
sys.path.append("/home/lucas/Documentos/NSI/eis/eispatterns")


from django.db import models
from should_dsl import should
from domain.resource.work_item import WorkItem
from domain.base.decorator import Decorator
from domain.node.person import Person
from domain.supportive.rule import rule
from domain.supportive.association_error import AssociationError
from domain.supportive.contract_matchers import be_decorated_by
from domain.node.machine import Machine
from domain.supportive.contract_error import ContractError
from bank_system.resources.loan_request import LoanRequest
from bank_system.resources.loan import Loan
from bank_system.rules.bank_system_rule_base import BankSystemRuleBase
from domain.supportive.rule_manager import RuleManager
from domain.resource.operation import operation
from should_dsl import should, ShouldNotSatisfied
from domain.node.node import Node
from domain.resource.operation import operation
from django.contrib.auth.models import User
import jsonpickle

a_machine = Machine()
a_person = Person()

################################################# DECORATOR: BANK ACCOUNT ##############################################################

# A classe ClientName é para a atribuição automática do nome do cliente na sua conta 

class ClientName(User):

    class Meta:
        proxy = True

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)


#############################################################

class BankAccountDecorator(models.Model, Decorator):
    '''Bank Account'''

    decoration_rules = ['should_be_instance_of_machine']
    statement = {}

    id = models.AutoField(primary_key=True)
    description = "A bank account" #models.CharField(max_length=100)
    #log area for already processed resources
    log_area = models.TextField(default = " ")
    balance =  models.IntegerField(default=0)
    #should it mask Machine.tag? decorated.tag = number?
    number = models.ForeignKey(User,related_name = 'number')
    restricted = models.BooleanField()
    average_credit = models.IntegerField(default=0)
    client = models.ForeignKey(ClientName, related_name = 'client')
    id_active_accounts = models.IntegerField(default=1)
    loan_request_times = models.IntegerField(default=0) 

    def self_decorate(self):
        self.decorate(a_machine)


    def save(self, *args, **kwargs):
        self.self_decorate()
        super(BankAccountDecorator, self).save(*args, **kwargs)
        Decorator.__init__(self)


    @operation(category = 'business')
    def deposit(self, value):
        ''' Makes a banking deposit '''
        deposit_count = 0
        deposit_count += 1
        deposit_number = 'deposit '+ str(deposit_count)
        self.average_credit += int(value)
        self.statement[deposit_number] = int(value)


    @operation(category = 'business')
    def draw(self, value):
        ''' Makes a banking draw '''
        draw_count = 0
        draw_count += 1
        draw_number = "draw " + str(draw_count)
        self.average_credit -= value
        self.statement[draw_number] = value


    @operation(category='business')
    def register_credit(self, value):
        ''' Register a credit in the balance '''
        register_credit_count = 0
        register_credit_count += 1
        register_credit_number = 'register_credit '+ str(register_credit_count)
        self.balance += value
        self.statement[register_credit_number] = int(value)


    @operation(category='business')
    def send_message_to_account_holder(self, message):
        ''' Sends a message to the account holder '''
        return message

    @operation(category='business')
    def transfer(self, value, a_bank_account):
        ''' Transfer a value to another account '''
        transfer_count = 0
        transfer_count += 1
        transfer_number = 'transfer '+ str(transfer_count)
        self.average_credit -= int(value)
        a_bank_account.average_credit += int(value)
        self.statement[transfer_number] = int(value)


    @operation(category='business')
    def check_the_statement(self):
        '''The statement of the account '''
        self.statement |should| have_at_least(1).key
        self.statement['average_credit'] = self.average_credit
        self.statement['balance'] = self.balance
        return self.statement


    def create_a_statement(self):
        '''Creating the statement of the account in the database'''
        self.log_area = jsonpickle.encode(self.statement)
        return self.log_area


############################################ DECORATOR: CREDIT ANALYST #############################################################

class CreditAnalystDecorator(models.Model, Decorator):
    '''Credit Analyst'''
    
    decoration_rules = ['should_be_instance_of_person']    #should_have_employee_decorator

    id = models.AutoField(primary_key=True)
    description = "An employee with credit analysis skills"
    register = models.CharField(max_length="20")
    loan_limit = models.IntegerField(default=0)

    def self_decorate(self):
            self.decorate(a_person)

    def save(self, *args, **kwargs):
        self.self_decorate()
        super(CreditAnalystDecorator, self).save(*args, **kwargs)
        Decorator.__init__(self)

    @operation(category='business')
    def create_loan_request(self, account, value):
        ''' creates a loan request '''
        loan_request = LoanRequest(account, value, self)
        #places the loan_request in the node's input area
        self.decorated.input_area[loan_request.account.number] = loan_request

    #stupid credit analysis, only for demonstration
    @operation(category='business')
    def analyse(self, loan_request_key):
        ''' automatically analyses a loan request '''
        if not self.decorated.input_area.has_key(loan_request_key): return False
        #move the request from the input_area to the processing_area
        self.decorated.transfer(loan_request_key,'input','processing')
        #picks the loan for processing
        loan_request = self.decorated.processing_area[loan_request_key]
        #automatically approves or not
        if not loan_request.account.restricted:
           if loan_request.account.average_credit*4 > loan_request.value:
               loan_request.approved = True
           else:
               loan_request.approved = False
        else:
           loan_request.approved = False
        #transfers the loan to the output_area
        self.decorated.transfer(loan_request_key,'processing','output')

    @operation(category='business')
    def create_loan(self, loan_request):
        ''' creates a loan '''
        loan = Loan(loan_request)
        #puts the new loan on the analyst's output_area, using analyst's register as key
        self.decorated.output_area[loan.loan_request.analyst.register] = loan

    @operation(category='business')
    def move_loan_to_account(self, loan_key, account):
        ''' moves the approved loan to the account '''
        try:
            loan = self.decorated.output_area[loan_key]
            loan |should| be_instance_of(Loan)
        except KeyError:
            raise KeyError("Loan with key %s not found in Analyst's output area" % loan_key)
        except ShouldNotSatisfied:
            raise ContractError('Loan instance expected, instead %s passed' % type(loan))
        try:
            Node.move_resource(loan_key, self.decorated, account.decorated)
        except ShouldNotSatisfied:
            raise ContractError('Bank Account instance expected, instead %s passed' % type(account))
        account.register_credit(loan.loan_request.value)

    def change_loan_limit(self, new_limit):
        self.loan_limit = new_limit

################################################# DECORATOR: EMPLOYEE ##############################################################

class EmployeeDecorator(models.Model, Decorator):
    
    '''A general purpose Employee decorator'''
    
    decoration_rules = ['should_be_instance_of_person']

    id = models.AutoField(primary_key=True)
    description = "Supplies the basis for representing employes"
    name = models.CharField(max_length='70')

    def self_decorate(self):
        self.decorate(a_person)


    def save(self, *args, **kwargs):
        self.self_decorate()
        super(EmployeeDecorator, self).save(*args, **kwargs)
        Decorator.__init__(self)

    def generate_register(self, register):
        ''' generates the register number for the employee '''
        self.register = register


################################################# DECORATOR: CLIENT ##############################################################

'''class ClientDecorator(User, Decorator):
    A general porpuse Client decorator
  
    decoration_rules = ['should_be_instance_of_person']

    def save(self, *args, **kwargs):
            super(ClientDecorator, self).save(*args, **kwargs)
            User.__init__(self)
            Decorator.__init__(self)

    class Meta:
       app_label = 'global_variables'

    def generate_register(self, register):
        generates the register number for the client
        self.register = register'''


################################################# DECORATOR: ATTENDANT ##############################################################

class AttendantDecorator(models.Model, Decorator):
    '''Attendant'''
    decoration_rules = ['should_be_instance_of_person']

    id = models.AutoField(primary_key=True)
    description = "An employee with attendant skills"
    name = models.CharField(max_length='40')

    def self_decorate(self):
        self.decorate(a_person)

    def save(self, *args, **kwargs):
        self.self_decorate()
        super(AttendantDecorator, self).save(*args, **kwargs)
        Decorator.__init__(self)

    def discount_check(self, a_check, a_bank_account_decorator):
        for account in a_bank_account_decorator.id_active_accounts:
            if  a_bank_account_decorator.number == a_check.account_number:
                if  a_bank_account_decorator.average_credit >= a_check.value:
                     a_bank_account_decorator.draw(a_check.value)
                else:
                    raise InsuficientFunds("Insuficient Funds")

class InsuficientFunds(Exception):
    pass


################################################# DECORATOR: CONTACT ##############################################################

class ContactDecorator(models.Model,Decorator):
    '''Contact'''

    decoration_rules = ['should_be_instance_of_machine']

    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length="50")
    last_name = models.CharField(max_length="50")
    emailUser = models.EmailField()
    telephone = models.CharField(max_length="20")
    comments = models.TextField()

    def self_decorate(self):
        self.decorate(a_machine)

    def save(self, *args, **kwargs):
        self.self_decorate()
        super(ContactDecorator, self).save(*args, **kwargs)
        Decorator.__init__(self)