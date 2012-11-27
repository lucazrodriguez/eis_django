import sys
sys.path.append("home/lucas/Documentos/NSI/eis/eispatterns-examples")
sys.path.append("/home/lucas/Documentos/NSI/eis/eispatterns")

from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.http import HttpResponse
from bank_system.models import *
from django.contrib.auth import authenticate, logout, login as authlogin
from django.template import RequestContext, Context, loader
from bank_system.resources.bill import Bill
from django.core.exceptions import ObjectDoesNotExist


def home(request):
    csrfContext = RequestContext(request)
    return render_to_response('home.html', csrfContext)


def login(request):

    if request.user.id:
        return render_to_response('logged.html',context_instance=RequestContext(request, {}))

    if request.POST:
        accountUser = request.POST.get('account')
        passwordUser = request.POST.get('password')
        u = authenticate(username=accountUser, password=passwordUser)
        if u is not None:
            if u.is_active:
                authlogin(request, u)

                if request.POST.get('next'):
                    return HttpResponseRedirect(request.POST.get('next'))

                return render_to_response('logged.html',locals(),context_instance=RequestContext(request, {}))
        
    return render_to_response('login.html',(),context_instance=RequestContext(request, {}))


def log_out(request):
    logout(request)
    csrfContext = RequestContext(request)
    return render_to_response('home.html',csrfContext)


def contact(request):

    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')
    telephone = request.POST.get('telephone')
    comments = request.POST.get('comments')

    if first_name and email and comments is not None:
        a_machine = Machine()
        contact = ContactDecorator.objects.create(first_name=first_name, last_name=last_name , emailUser=email , telephone=telephone , comments=comments)
        contact.decorate(a_machine)
        contact.save_base()
        return render_to_response('send.html',RequestContext(request))        

    return render_to_response('contact.html',locals(),context_instance=RequestContext(request, {}))


def balance(request):

    if not request.user.id or request.user.is_superuser == True:
        return render_to_response('logged_error.html',context_instance=RequestContext(request, {}))

    user = User.objects.get(username = request.user)
    account = BankAccountDecorator.objects.get(number = user)
    number = account.number
    client = account.client
    average_credit = account.average_credit
    balance = account.balance
    log = account.log_area

    return render_to_response('balance.html',locals(),context_instance=RequestContext(request, {}))


def transfer(request):

    if not request.user.id or request.user.is_superuser == True:
        return render_to_response('logged_error.html',context_instance=RequestContext(request, {}))

    if request.POST:
        accountNumber = request.POST.get('account_number')
        amountTransfer = request.POST.get('amount_transfer')
        user = User.objects.get(username = request.user)
        bank_account = BankAccountDecorator.objects.get(number = user)
        user = User.objects.get(username = accountNumber)
        the_other_bank_account = BankAccountDecorator.objects.get(number = user)
        
        if user == request.user :
            return render_to_response('transfer_error.html',context_instance = RequestContext(request,{}))

        bank_account.log_area += '/  / Transfer: ' + str(user) + ' Value: ' + str(amountTransfer) + "  /  /\n\n"
        bank_account.transfer(amountTransfer,the_other_bank_account)
        bank_account.save_base()
        the_other_bank_account.save_base()

        return render_to_response('sucess.html',context_instance = RequestContext(request,{}))

    return render_to_response('transfer.html',context_instance=RequestContext(request, {}))


def loans(request):

    if not request.user.id or request.user.is_superuser == True:
        return render_to_response('logged_error.html',context_instance=RequestContext(request, {}))

    if request.POST:

        RuleManager.rule_base = BankSystemRuleBase()
        user = User.objects.get(username = request.user)
        bank_account = BankAccountDecorator.objects.get(number = user)
        amount_loan = request.POST.get('loan')
        try:
            credit_analyst = CreditAnalystDecorator.objects.get(register = request.POST.get('analyst'))
        except (CreditAnalystDecorator.DoesNotExist):
            return render_to_response('loan_error.html',context_instance = RequestContext(request,{}))
        
        bank_account.log_area += '/  /  Loan: ' + str(amount_loan) + ' Credit Analyst: ' + str(credit_analyst.register) + "/  /\n\n"
        
        a_loan_request = LoanRequest(bank_account,amount_loan,credit_analyst)
        a_loan = Loan(a_loan_request)
        bank_account.save_base()

        return render_to_response('sucess.html',locals(),context_instance=RequestContext(request, {}))

    return render_to_response('loans.html',(),context_instance=RequestContext(request, {}))


def payments(request):

    if not request.user.id or request.user.is_superuser == True:
        return render_to_response('logged_error.html',context_instance=RequestContext(request, {}))
    
    if request.POST:

        RuleManager.rule_base = BankSystemRuleBase()
        user = User.objects.get(username = request.user)
        bank_account = BankAccountDecorator.objects.get(number = user)
        bill = request.POST.get('bill')
        payment = request.POST.get('number')
        amount_charged = request.POST.get('amount_charged')
        
        bank_account.log_area += '/  / Payment: ' + str(bill) + ' Value: ' + str(amount_charged) + ' Payed: ' + str(payment) + "/  /\n\n"
        
        bill_payment = Bill(bank_account,bill,payment,amount_charged)
        bank_account.save_base()

        return render_to_response('sucess.html',locals(),context_instance=RequestContext(request, {}))
        
    return render_to_response('payments.html',(),context_instance=RequestContext(request, {}))


def sucess(request):

    csrfContext = RequestContext(request)
    return render_to_response('sucess.html', csrfContext)

def about(request):

    csrfContext = RequestContext(request)
    return render_to_response('about.html', csrfContext)    