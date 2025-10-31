from django.shortcuts import render,redirect
from shop.models import Category,Product
from django.views import View
class Categoryview(View):
    def get(self,request):
        c=Category.objects.all()
        context={'categories':c}
        return render(request,'categories.html',context)

class Productview(View):
    def get(self,request,i):
        c=Category.objects.get(id=i)
        context={'category':c}
        return render(request,'products.html',context)


class ProductDetailView(View):
    def get(self,request,i):
        p = Product.objects.get(id=i)
        context = {'product': p}
        return render(request, 'productdetail.html',context)

from shop.forms import SignupForm,LoginForm,CategoryForm,ProductForm,StockForm
class RegisterView(View):
    def post(self, request):
        form_instance = SignupForm(request.POST)
        if form_instance.is_valid():
            form_instance.save()
            return redirect('shop:login')


    def get(self, request):
        form_instance = SignupForm()
        context = {'form': form_instance}
        return render(request, 'register.html', context)



from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
class UserloginView(View):
    def post(self, request):
        form_instance = LoginForm(request.POST)
        if form_instance.is_valid():
          u=form_instance.cleaned_data['username']
          p=form_instance.cleaned_data['password']
          user=authenticate(username=u,password=p)
          if user:
            login(request, user)
            return redirect('shop:categories')
          else:
            messages.error(request,'invalid user credentials')
            return render(request, 'login.html',{'form':form_instance})

    def get(self, request):
        form_instance = LoginForm()
        context={'form':form_instance}
        return render(request, 'login.html',context)


class UserlogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('shop:login')


class AddCategoryView(View):
    def post(self, request):
        form_instance = CategoryForm(request.POST, request.FILES)
        if form_instance.is_valid():
            form_instance.save()
            return redirect('shop:categories')
        else:
            context = {'form': form_instance}
            return render(request, 'addcategory.html', context)

    def get(self, request):
        form_instance = CategoryForm()
        context = {'form': form_instance}
        return render(request, 'addcategory.html', context)


class AddProductView(View):
    def post(self, request):
        print(request.POST)
        print(request.FILES)
        form_instance = ProductForm(request.POST, request.FILES)
        if form_instance.is_valid():
            form_instance.save()
            return redirect('shop:categories')


    def get(self, request):
        form_instance = ProductForm()
        context = {'form': form_instance}
        return render(request, 'addproduct.html', context)


class AddStockView(View):
    def post(self, request, i):
        if request.method == "POST":
            p = Product.objects.get(id=i)
            form_instance = StockForm(request.POST, instance=p)
            if form_instance.is_valid():
                form_instance.save()
                return redirect('shop:categories')

    def get(self, request, i):
        p = Product.objects.get(id=i)
        form_instance = StockForm(instance=p)
        context = {'form': form_instance}
        return render(request, 'addstock.html', context)









