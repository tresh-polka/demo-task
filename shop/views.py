from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Products, Users, Producers, Providers # Проверь, что эти модели есть в models.py
from .forms import ProductForm

def login_view(request):
    if request.method == 'POST':
        user_login = request.POST.get('login')
        user_password = request.POST.get('password')
        try:
            user = Users.objects.get(email=user_login, password=user_password)
            request.session['user_fio'] = f"{user.surname} {user.name} {user.father_name}"
            request.session['user_role'] = user.role.roles_name 
            return redirect('products_list')
        except Users.DoesNotExist:
            return render(request, 'shop/login.html', {'error': 'Неверный логин или пароль'})
    
    request.session.flush()
    return render(request, 'shop/login.html')

def products_list(request):
    products = Products.objects.all() 
    producers = Producers.objects.all()
    providers = Providers.objects.all()

    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) | 
            Q(product_description__icontains=search_query)
        )

    prod_id = request.GET.get('producer')
    if prod_id:
        products = products.filter(producer_id=prod_id)
        
    prov_id = request.GET.get('provider')
    if prov_id:
        products = products.filter(provider_id=prov_id)
    
    sort_val = request.GET.get('sort')
    if sort_val == 'price_asc':
        products = products.order_by('price')
    elif sort_val == 'price_desc':
        products = products.order_by('-price')
    elif sort_val == 'amount_asc':
        products = products.order_by('amount')
    elif sort_val == 'amount_desc':
        products = products.order_by('-amount')

    for p in products:
        p.final_price = p.price - (p.price * p.discunt / 100) if p.discunt > 0 else p.price
    
    return render(request, 'shop/products_list.html', {
        'products': products,
        'producers': producers,
        'providers': providers,
    })

def product_edit(request, pk=None):
    if request.session.get('user_role') != 'Администратор':
        return redirect('products_list')

    instance = get_object_or_404(Products, pk=pk) if pk else None
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('products_list')
    else:
        form = ProductForm(instance=instance)

    return render(request, 'shop/product_edit.html', {
        'form': form, 
        'instance': instance,
        'title': 'Редактирование' if pk else 'Добавление'
    })