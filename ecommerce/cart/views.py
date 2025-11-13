from http.client import responses
from itertools import product
from django.contrib import messages
from django.shortcuts import render,redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from shop.models import Product
from cart.models import Cart
from cart.forms import OrderForm
import razorpay


class AddtoCart(View):
    def get(self,request,i):
        p=Product.objects.get(id=i)
        u=request.user
        try:

            c=Cart.objects.get(user=u,product=p)  #checks whether the product already placed by the current user
            c.quantity+=1                         #for checks whether the product is there in the cart table
                                                  # if yes increments the quantity by 1
            c.save()
        except:
            c=Cart.objects.create(user=u,product=p,quantity=1)  #else creates a new cart record inside cart table
            c.save()
        return redirect('cart:cartview')

class CartView(View):
    def get(self,request):
        u=request.user
        c=Cart.objects.filter(user=u)
        total=0     #to find the total sum
        for i in c:
            total+=i.product.price*i.quantity
        context={'cart':c,'total':total}
        return render(request,'cart.html',context)


class CartDecrement(View):
    def get(self, request, i):
        u = request.user
        p = Product.objects.get(id=i)
        try:
            c = Cart.objects.get(user=u, product=p)
            if c.quantity > 1:
                c.quantity -= 1
                c.save()
            else:
                c.delete()
        except Cart.DoesNotExist:
            pass
        return redirect('cart:cartview')


class CartDelete(View):
    def get(self, request, i):
        u = request.user
        try:
            p = Product.objects.get(id=i)
            c = Cart.objects.get(user=u, product=p)
            c.delete()
        except Cart.DoesNotExist:
            pass
        return redirect('cart:cartview')




def checkstock(cart_items):
    stock = True
    for i in cart_items:
        if i.quantity > i.product.stock:
            stock = False
            break
        else:
            stock = True
    return stock

import uuid
class Checkout(View):


    def post(self, request):
        form_instance = OrderForm(request.POST)
        if form_instance.is_valid():
            o = form_instance.save(commit=False)
            u = request.user
            o.user = u
            c = Cart.objects.filter(user=u)
            total = 0
            for i in c:
                total += i.product.price * i.quantity
            o.amount = total
            o.save()
            if(o.payment_method=="online"):
                  #razorpay client connection
                  client=razorpay.Client(auth=('rzp_test_RckwxJzLKWz5JA','jecLV6UsHFWZRvgqaOrcGSBf'))
                  print(client)
                  #place order
                  response_payment=client.order.create(dict(amount=total*100,currency='INR'))
                  print(response_payment)
                  id=response_payment['id']
                  o.order_id=id
                  o.save()
                  context={'payment':response_payment}
                  return render(request, 'payment.html',context)

            else:  #ORDER COD
                o.is_ordered = True
                uid = uuid.uuid4().hex[:14]
                id='order_COD'+uid  #manually creates orderid for COD orders using uuid module
                o.order_id=id
                o.save()

                for i in c:   # Move cart items to Order_items
                    items= Order_items.objects.create(order=o, product=i.product, quantity=i.quantity)
                    items.save()
                    items.product.stock -= items.quantity    # Reduce stock
                    items.product.save()

                c.delete()     # Delete items from cart


            return render(request, 'payment.html')

    def get(self, request):
            u = request.user
            c = Cart.objects.filter(user=u)
            stock = checkstock(c)
            form_instance = OrderForm()
            context = {'form': form_instance}
            if stock:
                return render(request, 'checkout.html', context)
            else:
                messages.error(request, "Currently items not available,can't place order")
                return render(request, 'checkout.html', context)



#After payment completion razorpay redirects into payment_success view
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib.auth import login
from cart.models import Order,Order_items
#to avoid csrf verification we use csrf_exempt
@method_decorator(csrf_exempt,name="dispatch")
class Payment_success(View):
    def post(self,request,i):      # here i represents the username
                                   #To add  user into the current session again
        u=User.objects.get(username=i)
        login(request,u)           #adds the user object u into session
        response=request.POST      #after payment razorpay sends payment details into success view as response
        print(response)
        id=response['razorpay_order_id']
        print(id)

        #Order
        order=Order.objects.get(order_id=id)
        order.is_ordered=True          #after successful completion of order
        order.save()

        #Order Items
        c=Cart.objects.filter(user=u)
        for i in c:
            o=Order_items.objects.create(order=order,product=i.product,quantity=i.quantity)
            o.save()
            o.product.stock-=o.quantity
            o.product.save()

        #Cart deletion
        c.delete()
        return render(request,'payment_success.html')

class Orders(View):
    def get(self,request):
        u=request.user
        o=Order.objects.filter(user=u,is_ordered=True)
        context={'orders':o}
        return render(request,'orders.html',context)