from django.shortcuts import render, redirect
from .forms import UserRegistrationForm # Bạn phải tạo file forms.py

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save() # Lưu User mới vào DB
            return redirect('login') # Chuyển hướng đến trang login
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})
