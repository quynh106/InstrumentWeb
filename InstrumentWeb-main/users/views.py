# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm 

def user_login(request):
    """
    Xử lý logic đăng nhập và chuyển hướng về trang chủ Store.
    """
    # 1. Nếu đã đăng nhập, chuyển hướng đi ngay
    if request.user.is_authenticated:
        return redirect('products:home') 

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Chuyển hướng về trang được chỉ định bởi LOGIN_REDIRECT_URL ('products:home')
                # hoặc tham số 'next' nếu có
                return redirect(request.GET.get('next') or 'products:home') 
            else:
                form.add_error(None, "Tên đăng nhập hoặc mật khẩu không đúng.")
    else:
        # GET request: hiển thị form trống
        form = AuthenticationForm()
        
    context = {'form': form}
    return render(request, 'users/login.html', context)