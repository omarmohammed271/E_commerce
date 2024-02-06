from django.shortcuts import redirect, render,get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from store.models import Product
from .models import Cart,CartItem,Coupon

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.creat()
    return cart

def add_cart(request,product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )   
        cart.save()
    try:
        cart_item = CartItem.objects.get(product=product,cart=cart) 
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            cart = cart,
            quantity=1
        )         
        cart_item.save()
    return redirect('cart:cart')       

def remove_cart(request,product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product,id=product_id)
    cart_item = CartItem.objects.get(product=product,cart=cart)
    if cart_item.quantity>=1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart:cart')    
    
def remove_cart_item(request,product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product,id=product_id)
    cart_item = CartItem.objects.get(product=product,cart=cart)
    cart_item.delete()
    return redirect("cart:cart")

def cart(request,total=0,quantity=0,cart_items=None,discount=0):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price) * (cart_item.quantity)
            quantity += cart_item.quantity    
        shipping = 20
        if request.method == "POST":
            coupon = request.POST['coupon']
            get_ratio = get_object_or_404(Coupon,value=coupon)
            if get_ratio.is_active == True:
                discount = (total + shipping )  * (get_ratio.ratio/100)
                grand_total = (total + shipping ) - discount  
            else:    
                grand_total = total + shipping    
        else:    
            grand_total = total + shipping    
    except ObjectDoesNotExist:
        pass        
    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'grand_total' :grand_total,
        'shipping' : shipping,
        'discount' : discount,
    }    
    return render(request,'store/cart.html',context)