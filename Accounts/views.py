from django.shortcuts import render, Http404, redirect
from django.contrib.auth.models import auth, User
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# Create your views here.
def login(request):
    try:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user is None:
                messages.info(request, 'Invalid credentials')
                return redirect('login')
            auth.login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'accounts/login.html')
    except Exception as e:
        raise Http404(e)


def signup(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if password1 == password2:
                if User.objects.filter(username=username).exists():
                    messages.info(request, 'Username already exists')
                    return redirect('signup')
                elif User.objects.filter(email=email).exists():
                    messages.info(request, 'Email already exists')
                    return redirect('signup')
                else:
                    user = User.objects.create_user(username=username, password=password1, email=email)
                    user.save()
                    messages.info(request, 'Account created successfully..!')
                    return redirect('login')
            else:
                messages.info(request, 'Password do not matched..!')
                return redirect('signup')
        else:
            return render(request, 'accounts/register.html')
    except Exception as e:
        raise Http404(e)


@login_required
def logout(request):
    try:
        auth.logout(request)
        return redirect('home')
    except Exception as e:
        raise Http404(e)
