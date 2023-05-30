from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from .forms import OrderForm, CreatUserForm, CustomerForm
from django.forms import inlineformset_factory
from .filters import OrderFilter
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .decorators import unauthenticated_user, allowed_users, admin_only
# flash message
from django.contrib import messages
# authentication login logout
from django.contrib.auth import authenticate, login, logout

#decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group


# Create your views here.


@unauthenticated_user
def registerPage(request):
    
    form = CreatUserForm()
    if request.method == 'POST':
        form = CreatUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            messages.success(request, 'Account was created for ' + username)
            return redirect('login')

    context = {'form': form}
    return render(request, 'accounts/register.html', context)

@unauthenticated_user
def loginPage(request):
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else: 
            messages.info(request, 'Username or Password is incorrect!')

    context = {}
    return render(request, 'accounts/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    orders = request.user.customer.order_set.all()

    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {'orders':orders, 'total_orders': total_orders, 'delivered':delivered, 'pending':pending}
    return render(request, 'accounts/user.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES ,instance=customer)
        if form.is_valid():
            form.save()
          
        
    context = {'form':form}
    return render(request, 'accounts/account_settings.html', context)

@login_required(login_url='login')
@admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()

    total_customers = customers.count()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {'orders': orders, 'customers': customers, 'total_customers':total_customers, 'total_orders': total_orders, 'delivered':delivered, 'pending':pending}
    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()

    p = Paginator(products, 4)
    page = request.GET.get('page')
    products = p.get_page(page)


    try:
        products = p.page(page)
    except PageNotAnInteger:
        page = 1
        products = p.page(page)
    except EmptyPage:
        page = p.num_pages
        products = p.page(page)

    leftIndex = (int(page) - 2)
    if leftIndex < 1:
        leftIndex = 1
    
    rightIndex = (int(page) + 3)
    if rightIndex > p.num_pages:
        rightIndex = p.num_pages + 1


    custom_range = range(leftIndex, rightIndex)
    
    context={'products': products, 'custom_range': custom_range}
    return render(request, 'accounts/products.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customers(request, pk):
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all()
    orders_count = orders.count() 

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    context = {'customer': customer, 'orders': orders, 'orders_count':orders_count, 'myFilter': myFilter}
    return render(request, 'accounts/customer.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request, pk):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=5)
    customer = Customer.objects.get(id=pk)
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    
    # form = OrderForm(initial={'customer': customer})
    if request.method == 'POST':
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')
        

    context= {'formset': formset}
    return render(request, 'accounts/order_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):        
    order = Order.objects.get(id=pk)

    form = OrderForm(instance=order)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')

    context= {'form': form}
    return render(request, 'accounts/order_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)

    if request.method == "POST":
        order.delete()
        return redirect('/')
    
    context = {'item': order}
    return render(request, 'accounts/delete.html', context)



