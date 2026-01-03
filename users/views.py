from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages

# 1. Chức năng Đăng ký
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Lưu người dùng mới vào Database
            login(request, user) # Đăng ký xong tự động đăng nhập luôn cho tiện
            messages.success(request, f'Tài khoản {user.username} đã được tạo thành công!')
            return redirect('home') # Chuyển hướng về trang chủ (hoặc trang bạn muốn)
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

# 2. Chức năng Đăng nhập
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Bạn đã đăng nhập bằng tên {username}.")
                return redirect('home')
            else:
                messages.error(request, "Sai tên đăng nhập hoặc mật khẩu.")
        else:
            messages.error(request, "Thông tin đăng nhập không hợp lệ.")
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

# 3. Chức năng Đăng xuất
def logout_view(request):
    logout(request)
    messages.info(request, "Bạn đã đăng xuất thành công.")
    return redirect('login')
