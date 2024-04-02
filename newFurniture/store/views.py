from .forms import CustomUserCreationForm
from django.shortcuts import render,redirect
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth import get_user
from django.contrib.auth import logout,authenticate
from django.core.mail import send_mail
from newFurniture import settings
from django.http import JsonResponse
import json
import datetime
from .utlis import cartData,guestOrder
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Customer







# Create your views here.
def main(request):
    return render(request,'store/main.html')
		
def store1(request):
    data =cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    
    products = Product.objects.all()
    context = {'products':products,'cartItems':cartItems}
    return render(request, 'store/store.html',context)

def cart(request):
    data =cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
        
    context = {'items':items,'cartItems':cartItems,'order':order}
    return render(request, 'store/cart.html',context)


@login_required(login_url='login')
@csrf_exempt
def checkout(request):
    data =cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

       
    context={'items':items,'order':order,'cartItems':cartItems}
    return render(request, 'store/checkout.html',context)


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a Customer instance for the newly created user
            Customer.objects.create(user=user, name=user.username, email=user.email)
            auth_login(request, user)
            messages.success(request, "Registration successful. You are now logged in.")
            return redirect('/')  # Replace 'home' with your desired URL
        else:
            messages.error(request, "Registration failed. Please correct the errors.")
    else:
        form = UserCreationForm()
    return render(request, 'store/signup.html', {'form': form})


def login(request):
    if request.method =='POST' :
        user=request.POST.get('username')
        pass1=request.POST.get('password')
        user=authenticate(username=user,password=pass1)
        
        if user:
            auth_login(request, user)
            messages.success(request,"You have Loged in Successfully")
            return redirect('/')
        else:
            messages.error(request,"username and Password is incorrect!")

    return render(request, 'store/login.html')




def logoutpage(request):
    logout(request)
    messages.error(request,'You have logged out!')
    return redirect('/')

def about(request):
    user = get_user(request)
    return render(request,'store/about.html',{'user':user})

def contact(request):
    user=get_user(request)
    if request.method=='POST':
        newfeedback=feedbackForm(request.POST)
        if newfeedback.is_valid():
            newfeedback.save()
            print("Your feedback has been submitted!")
            messages.success(request,'Your feedback has been submitted!')
            #Email Sending
            sub=request.POST['subject']
            msg=f'Dear User!\n\nThanks for your feedback\nWe will connect shortly!\n\nThank & Regards!\nWebApp Team\n+91 6351959948 | helpwebapps@.com | www.webapp.com'
            from_ID=settings.EMAIL_HOST_USER
            to_ID=[request.POST['email']]
            send_mail(subject=sub,message=msg,from_email=from_ID,recipient_list=to_ID)


            return redirect('store/home.html')
        else:
            print(newfeedback.errors)
    return render(request,'store/contact.html',{'user':user})



def home(request):
    return render(request,'store/home.html')

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
	    orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    
    orderItem.save()

    if orderItem.quantity <= 0:
	    orderItem.delete()
    return JsonResponse('Item was added', safe=False)


@csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data=json.loads(request.body)
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        
    else:

        customer, order = guestOrder(request, data) 
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shipping == True:

            ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
                )
    
    return JsonResponse('Payment submitted..', safe=False)

def productDetail(request,pk):
    product = Product.objects.get(id=pk)


    return render(request,'store/productDetail.html',{'product':product})