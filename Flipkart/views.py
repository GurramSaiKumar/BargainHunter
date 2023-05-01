import math
from decimal import *

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, Http404, redirect, HttpResponseRedirect

from Flipkart.models import PriceDrop


# Create your views here.
def home(request):
    return render(request, 'index.html', {})


def dashboard(request):
    try:
        items = PriceDrop.objects.filter(user=request.user)  # Getting user data
    # global prices
    except PriceDrop.DoesNotExist:
        raise Http404("Page doesn't Exist")
    # import pdb; pdb.set_trace()
    prices = []

    # Grab the current price from DB links/urls of added products
    # def check_price(items):
    for i in range(len(items)):
        response = requests.get(items[i].url)
        soup = BeautifulSoup(response.text, 'html.parser')
        price = soup.find('div', class_="_30jeq3 _16Jk6d").getText()
        price = float(price[1:])
        prices.append(price)

        old_price = items[i].curr_price
        price_change = old_price - Decimal(price)  # calculating price change
        pct_10 = math.ceil(old_price * Decimal((10 / 100)))  # Calculating 10%

        # Price Coomparision
        if pct_10 <= price_change:
            # sending emails
            subject = 'Alert: Price Dropped To 10%'
            message = "Hey, " + request.user.username + " \nYou added a product from flipkart in Price Drop website, Now its time to Grab your product. " + '\nProduct Title :' + \
                      items[i].title + '\n Current price: ' + '₹' + str(price) + '\n Old Price: ' + '₹' + str(
                old_price) + "\n Check The product, Link is Here: " + items[i].url
            to_email = [request.user.email]
            send_mail(subject, message, settings.EMAIL_HOST_USER, to_email, fail_silently=False)

    #TODO: monitor this
    return render(request, 'dashboard.html', {'items': zip(items, prices)})


@login_required
def add_url(request):
    try:
        if request.method == 'POST':
            url = request.POST['url']
            # import pdb; pdb.set_trace()
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('span', class_="B_NuCI").getText()
            price = soup.find('div', class_="_30jeq3 _16Jk6d").getText()
            price = float(price[1:])
            data = PriceDrop(title=title, url=url, curr_price=price)
            data.user = request.user
            data.save()
    except Exception:
        raise Http404("Page doesn't Exist")

    return redirect('dashboard')


@login_required
def delete(request, id):
    item = PriceDrop.objects.get(id=id)
    try:
        item.delete()
    except Exception:
        return HttpResponseRedirect('Item not found')
    return redirect('dashboard')
