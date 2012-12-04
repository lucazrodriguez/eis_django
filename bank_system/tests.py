import sys
sys.path.append("home/lucas/Documentos/NSI/eis/eispatterns-examples")
sys.path.append("/home/lucas/Documentos/NSI/eis/eispatterns")

from django.utils import unittest
from should_dsl import should, should_not
from domain.supportive.association_error import AssociationError
from bank_system.models import *
from bank_system.resources.check import Check
from bank_system.resources.bill import Bill

################################################# BANK ACCOUNT ###################################################################

class BankAccountDecoratorTestCase(unittest.TestCase):

    def setUp(self):
        self.a_client = Person()
        self.a_machine = Machine()
        self.a_number = User.objects.model(pk = 1 , username = '11111-1', email = 'First@email', first_name = 'First', last_name = 'Last')
        self.client_name = ClientName(pk = 1)
        self.a_number.decorate(self.a_client)
        self.a_bank_account_decorator = BankAccountDecorator.objects.create(number = self.a_number, client = self.client_name)
        self.another_number = User.objects.model(pk =2 ,username = '22222-2', email = 'Second@email', first_name = 'Second', last_name = 'Last')
        self.another_client_name = ClientName(pk = 2)
        self.another_number.decorate(self.a_client)
        self.another_bank_account_decorator = BankAccountDecorator.objects.create(number = self.another_number, client = self.another_client_name)

    def testVerify_inclusion_of_a_bank_account_decorator(self):
        self.a_bank_account_decorator.number |should| equal_to(self.a_number)
        self.another_bank_account_decorator.number |should| equal_to(self.another_number)

    def testDecorates_a_machine(self):
        #should work
        self.a_bank_account_decorator.decorate(self.a_machine)
        self.another_bank_account_decorator.decorate(self.a_machine)
        self.a_number.decorated |should| be(self.a_client)
        self.another_number.decorated |should| be(self.a_client)
        self.another_bank_account_decorator.decorated |should| be(self.a_machine)
        self.another_bank_account_decorator.decorated |should| have(1).decorators
        self.a_bank_account_decorator.decorated |should| be(self.a_machine)
        self.a_bank_account_decorator.decorated |should| have(1).decorators
        #should fail
        decorate, _, _ = self.a_bank_account_decorator.decorate('I am not a machine')
        decorate |should| equal_to(False)
        decorate, _, _ = self.another_bank_account_decorator.decorate('I am not a machine')
        decorate |should| equal_to(False)

    def testRegisters_a_credit(self):
        self.a_bank_account_decorator.balance = 100
        self.a_bank_account_decorator.register_credit(50)
        self.a_bank_account_decorator.balance |should| equal_to(150)
        self.a_bank_account_decorator.statement |should| have (3).key
        self.another_bank_account_decorator.balance = 100
        self.another_bank_account_decorator.register_credit(50)
        self.another_bank_account_decorator.balance |should| equal_to(150)
        self.another_bank_account_decorator.statement |should| have (3).key

    def test_sends_a_message_to_the_account_holder(self):
        message = 'This is a message'
        self.a_bank_account_decorator.send_message_to_account_holder(message) |should| equal_to(message)
        self.another_bank_account_decorator.send_message_to_account_holder(message) |should| equal_to(message)

    def test_check_the_client(self):
        #should work
        self.a_client |should| have(1).decorators
        self.a_bank_account_decorator.client |should| be(self.client_name)
        self.another_bank_account_decorator.client |should| be(self.another_client_name)

    def test_realize_a_banking(self):
        self.a_bank_account_decorator.decorate(self.a_machine)
        self.a_bank_account_decorator.deposit(100)
        self.a_bank_account_decorator.draw(25)
        self.a_bank_account_decorator.transfer(50,self.another_bank_account_decorator)
        self.a_bank_account_decorator.average_credit |should| be(25)
        self.another_bank_account_decorator.average_credit |should| be(50)
        self.a_bank_account_decorator.check_the_statement()
        self.a_bank_account_decorator.statement |should| have(6).key
        self.another_bank_account_decorator.statement |should| have(6).key
        self.a_bank_account_decorator.create_a_statement() |should| be_kind_of(str)

################################################# CREDIT ANALYST ###################################################################

class CreditAnalystDecoratorTestCase(unittest.TestCase):

    def setUp(self):
        #set the rule base
        RuleManager.rule_base = BankSystemRuleBase()
        #
        self.a_credit_analyst_decorator = CreditAnalystDecorator.objects.create(register='12345-6')
        #test doubles won't work given type checking rules, using classic
        self.a_person = Person()
        self.a_client = Person()
        self.a_number = User.objects.model(pk = 1, username = '11111-1', email = 'First@email', first_name = 'First', last_name = 'Last')
        self.client_name = ClientName(pk = 1)
        self.a_number.decorate(self.a_client)
        self.an_account = BankAccountDecorator.objects.create(number = self.a_number, client = self.client_name)

    def test_decorates_a_person(self):
        #should fail
        decorate, _, _ = self.a_credit_analyst_decorator.decorate('im not a person')
        decorate |should| equal_to(False)
        #should work
        an_employee_decorator = EmployeeDecorator()
        an_employee_decorator.decorate(self.a_person)
        self.a_credit_analyst_decorator.decorate(self.a_person)
        self.a_credit_analyst_decorator.decorated |should| be(self.a_person)
        self.a_credit_analyst_decorator.decorated |should| have(2).decorators

    def test_creates_a_loan_request(self):
        an_employee_decorator = EmployeeDecorator()
        an_employee_decorator.decorate(self.a_person)
        self.a_credit_analyst_decorator.decorate(self.a_person)
        self.a_credit_analyst_decorator.create_loan_request(self.an_account, 10000)
        self.a_person.input_area |should| contain(self.a_number)

    def test_analyses_a_loan_request(self):
        an_employee_decorator = EmployeeDecorator()
        an_employee_decorator.decorate(self.a_person)
        #Stub removed, from now on Node really transfers resources internally
        self.a_credit_analyst_decorator.decorate(self.a_person)
        self.an_account.average_credit = 5000
        #should approve
        self.a_credit_analyst_decorator.create_loan_request(self.an_account, 10000)
        self.a_credit_analyst_decorator.analyse(self.an_account.number)
        self.a_credit_analyst_decorator.decorated.output_area[self.a_number].approved |should| equal_to(True)
        #should refuse
        self.a_credit_analyst_decorator.create_loan_request(self.an_account, 50000)
        self.a_credit_analyst_decorator.analyse(self.an_account.number)
        self.a_credit_analyst_decorator.decorated.output_area[self.a_number].approved |should| equal_to(False)

    def test_creates_a_loan(self):
        an_employee_decorator = EmployeeDecorator()
        an_employee_decorator.decorate(self.a_person)
        loan_request = LoanRequest(self.an_account, 7000, self.a_credit_analyst_decorator)
        self.a_credit_analyst_decorator.decorate(self.a_person)
        self.a_credit_analyst_decorator.decorated.output_area[self.an_account.number] = loan_request
        #creates a machine to be decorated by the account - will need to check its processing_area
        a_machine = Machine()
        self.an_account.decorate(a_machine)
        #creates the loan
        self.a_credit_analyst_decorator.create_loan(loan_request)
        #loan key is the analyst's register
        self.a_credit_analyst_decorator.decorated.output_area.values() |should| have_at_least(1).loan
        self.a_credit_analyst_decorator.decorated.output_area |should| include(self.a_credit_analyst_decorator.register)

    def test_moves_the_loan_to_an_account(self):
        #prepares the person Node
        an_employee_decorator = EmployeeDecorator()
        an_employee_decorator.decorate(self.a_person)
        self.a_credit_analyst_decorator.decorate(self.a_person)
        #prepares a Loan
        loan_request = LoanRequest(self.an_account, 7000, self.a_credit_analyst_decorator)
        self.a_credit_analyst_decorator.decorated.output_area[self.an_account.number] = loan_request
        self.a_credit_analyst_decorator.create_loan(loan_request)
        #should go wrong
        passing_a_wrong_key = 'wrong key'
        (self.a_credit_analyst_decorator.move_loan_to_account, passing_a_wrong_key, self.an_account) |should| throw(KeyError)
        passing_a_non_account = 'I am not an account'
        (self.a_credit_analyst_decorator.move_loan_to_account, self.an_account.number, passing_a_non_account) |should| throw(ContractError)
        #prepares the account
        a_machine = Machine()
        self.an_account.decorate(a_machine)
        #should work
        loan_key = self.a_credit_analyst_decorator.register
        self.a_credit_analyst_decorator.move_loan_to_account(loan_key, self.an_account)
        self.an_account.decorated.input_area |should| include(loan_key)
        self.an_account.balance |should| equal_to(7000)

    def test_changes_its_loan_limit(self):
        self.a_credit_analyst_decorator.change_loan_limit(100000)
        self.a_credit_analyst_decorator.loan_limit |should| be(100000)

################################################# EMPLOYEE ###################################################################

class EmployeeDecoratorTestCase(unittest.TestCase):


    def setUp(self):
        self.an_employee_decorator = EmployeeDecorator.objects.create(name="Steve")
        #test doubles won't work given type checking rules, using classic
        self.a_person = Person()


    def test_decorates_a_person(self):
        #should work
        self.an_employee_decorator.decorate(self.a_person)
        self.an_employee_decorator.decorated |should| be(self.a_person)
        self.an_employee_decorator.decorated |should| have(1).decorators
        #should fail
        decorate,_,_ = self.an_employee_decorator.decorate('I am not a person')
        decorate |should| equal_to(False)


    def test_generates_register(self):
        self.an_employee_decorator.generate_register('123456-7')
        self.an_employee_decorator.register |should| equal_to('123456-7')

################################################# CLIENT ###################################################################

'''class ClientDecoratorTestCase(unittest.TestCase):

    def setUp(self):
        self.a_client_decorator = ClientDecorator()
        self.a_client = Person()

    def test_decorates_a_person(self):
        #should work
        self.a_client_decorator.decorate(self.a_client)
        self.a_client_decorator.decorated |should| be(self.a_client)
        self.a_client |should| have(1).decorators

    def test_generates_a_register(self):
        self.a_client_decorator.generate_register('12345-6')
        self.a_client_decorator.register |should| equal_to('12345-6')'''

################################################# LOAN REQUEST ###################################################################

class LoanRequestTestCase(unittest.TestCase):

    def setUp(self):
        self.a_client = Person()
        self.a_machine = Machine()

    def test_check_associations_with_bank_account_and_credit_analyst(self):
        #set the rule base
        RuleManager.rule_base = BankSystemRuleBase()
        #
        self.a_number = User.objects.model(pk = 1, username = '11111-1', email = 'First@email', first_name = 'First', last_name = 'Last')
        self.client_name = ClientName(pk = 1)
        self.an_account = BankAccountDecorator.objects.create(number = self.a_number, client = self.client_name)
        self.an_account.decorate(self.a_client)
        an_analyst = CreditAnalystDecorator.objects.create(register='abcde-f')
        (LoanRequest, 'I am not an account', 123, an_analyst) |should| throw(AssociationError)
        (LoanRequest, self.an_account, 123, 'I am not an analyst') |should| throw(AssociationError)
        (LoanRequest, self.an_account, 123, an_analyst) |should_not| throw(AssociationError)

################################################# LOAN ###################################################################

class LoanTestCase(unittest.TestCase):

    def test_check_association_with_loan_request(self):
        #set the rule base
        RuleManager.rule_base = BankSystemRuleBase()
        #
        (Loan, 'I am not a loan request') |should| throw(AssociationError)
        a_credit_analyst = CreditAnalystDecorator.objects.create(register='12345-6')
        self.a_number = User.objects.model(pk = 1, username = '12345-6', email = 'First@email', first_name = 'First', last_name = 'Last')
        self.client_name = ClientName(pk = 1)
        self.an_account = BankAccountDecorator.objects.create(number = self.a_number, client = self.client_name)
        a_loan_request = LoanRequest(self.an_account, 7000, a_credit_analyst)
        (Loan, a_loan_request) |should_not| throw(AssociationError)

################################################# BILL PAYMENT ###########################################################

class BillTestCase(unittest.TestCase):

    def setUp(self):
        self.a_number = User.objects.model(pk = 1, username = '12345-6', email = 'First@email', first_name = 'First', last_name = 'Last')
        self.client_name = ClientName(pk = 1)
        self.an_account = BankAccountDecorator.objects.create(number = self.a_number, client = self.client_name)

    def test_check_associations_with_bank_account_and_bill(self):
        #set the rule base
        RuleManager.rule_base = BankSystemRuleBase()
        #
        a_bill = 'House bill'
        (Bill, 'I am not an account', a_bill, 100, 100) |should| throw(AssociationError)
        (Bill, self.an_account, 'I am not a bill',100, 100) |should| throw (AssociationError)
        (Bill, self.an_account, a_bill, 100, 50) |should| throw (AssociationError)
        (Bill, self.an_account, a_bill, 50, 100) |should| throw(AssociationError)
        (Bill, self.an_account, a_bill, 100, 100) |should_not| throw(AssociationError)

    def test_check_a_bill_payment(self):
        #set the rule base
        RuleManager.rule_base = BankSystemRuleBase()
        #
        a_bill = 'Credit card bill'
        self.a_bill_payment = Bill(self.an_account, a_bill, 5000, 5000)
        (Bill, self.a_bill_payment) |should_not| throw(AssociationError)

################################################# ATTENDANT ###################################################################

class AttendantDecoratorTestCase(unittest.TestCase):

    def setUp(self):
        self.an_employee_decorator = EmployeeDecorator()
        self.an_attendant_decorator = AttendantDecorator()
        self.an_attendant = Person()

    def test_decorates_a_person(self):
        self.an_employee_decorator.decorate(self.an_attendant)
        self.an_attendant_decorator.decorate(self.an_attendant)
        self.an_attendant_decorator.decorated |should| be(self.an_attendant)
        self.an_attendant |should| have(2).decorators

    def test_gets_a_check(self):
        #Receiving a check
        self.an_employee_decorator.decorate(self.an_attendant)
        self.an_attendant_decorator.decorate(self.an_attendant)
        a_check = Check(id_="123", account_number="1234-5", value=10.0)
        #           Verifing check attributes
        #-------------------------------------------------
        a_check.id_ |should| equal_to("123")
        a_check.account_number |should| equal_to("1234-5")
        a_check.value |should| equal_to(10.0)
        #-------------------------------------------------

    def test_discount_a_check(self):
        #Discounting a check, it should work!
        self.a_machine = Machine()
        self.a_client = Person()
        self.a_number = User.objects.model(pk = 1, username = '12345-6', email = 'First@email', first_name = 'First', last_name = 'Last')
        self.client_name = ClientName(pk = 1)
        self.a_number.decorate(self.a_client)        
        self.a_bank_account_decorator = BankAccountDecorator.objects.create(number = self.a_number, client = self.client_name, id_active_accounts= "2")
        self.a_bank_account_decorator.decorate(self.a_machine)
        self.a_bank_account_decorator.deposit(100)
        self.a_bank_account_decorator.average_credit |should| equal_to(100)
        self.a_check = Check(id_="123", account_number = self.a_number, value = 10)
        self.an_attendant_decorator.discount_check(self.a_check, self.a_bank_account_decorator)
        self.a_bank_account_decorator.average_credit |should| equal_to(90)
        #It should fail!
        self.a_bank_account_decorator = BankAccountDecorator.objects.create(client = self.client_name, number = self.a_number, id_active_accounts= "2")
        self.a_bank_account_decorator.average_credit = 100
        self.a_bank_account_decorator.decorate(self.a_machine)
        self.a_check = Check(id_="123", account_number= self.a_number, value=110)
        (self.an_attendant_decorator.discount_check, self.a_check, self.a_bank_account_decorator) |should| throw (InsuficientFunds)
        self.a_bank_account_decorator.average_credit |should| equal_to(100)

    def test_tearDown(self):
        BankAccountDecorator = []