from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile, Stock, FollowChart
from datetime import datetime
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot


@login_required(login_url='signin')
def home(request):
    feed = []
    followed_stocks = FollowChart.objects.filter(username=request.user.username)
    for stock in followed_stocks:
        ticker = Stock.objects.get(id=stock.chart_id).ticker
        stock_data = yf.download(ticker, start='2023-01-01', end=datetime.today().strftime('%Y-%m-%d'), interval='1d')

        # Create the candlestick chart
        fig = go.Figure(data=[go.Candlestick(x=stock_data.index,
                                             open=stock_data['Open'],
                                             high=stock_data['High'],
                                             low=stock_data['Low'],
                                             close=stock_data['Close'])])

        # Update layout
        fig.update_layout(title=f'{ticker}/USD',
                          xaxis_rangeslider_visible=False)

        # Convert the figure to a div string
        plot_div = plot(fig, output_type='div')
        feed.append(plot_div)

    return render(request, 'home.html', context={'charts': feed})


def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password2 == password:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Ten email jest zajęty')
                return  redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Nazwa użytkownia jest zajęta')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Hasła nie są takie same')
            return redirect('signup')
    else:
        return render(request, 'signup.html')


def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user is None:
            messages.info(request, 'Niepoprawna nazwa użytkownika lub hasło')
            return redirect('signin')
        else:
            auth.login(request, user)
            return redirect('/')
    else:
        return render(request, 'signin.html')


@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')


@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == "POST":

        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        return redirect('settings')
    return render(request, 'settings.html', {'user_profile': user_profile})



def chart(request, pk):
    username = request.user.username
    if FollowChart.objects.filter(chart_id=pk, username=username).first():
        button_text = "Unfollow"
    else:
        button_text = "Follow"
    context = {}
    messages = []
    stock_id = pk
    stock = get_object_or_404(Stock, id=pk)
    ticker_symbol = stock.ticker
    if request.method == "POST":
        start = request.POST['start-date']
        end = request.POST['end-date']
        interval = request.POST['interval']
        try:
            stock_data = yf.download(ticker_symbol, start=start, end=end, interval=interval)

            # Create the candlestick chart
            fig = go.Figure(data=[go.Candlestick(x=stock_data.index,
                                                 open=stock_data['Open'],
                                                 high=stock_data['High'],
                                                 low=stock_data['Low'],
                                                 close=stock_data['Close'])])

            # Update layout
            fig.update_layout(title=f'{stock.ticker}/USD',
                              xaxis_rangeslider_visible=False)

            plot_div = plot(fig, output_type='div')
        except Exception as e:
            messages.append(f"An unexpected error occurred: {e}")
    else:
        try:
            stock_data = yf.download(ticker_symbol, start='2023-01-01', end=datetime.today().strftime('%Y-%m-%d'), interval='1d')

            # Create the candlestick chart
            fig = go.Figure(data=[go.Candlestick(x=stock_data.index,
                                                 open=stock_data['Open'],
                                                 high=stock_data['High'],
                                                 low=stock_data['Low'],
                                                 close=stock_data['Close'])])

            # Update layout
            fig.update_layout(title=f'{stock.ticker}/USD',
                              xaxis_rangeslider_visible=False)

            plot_div = plot(fig, output_type='div')
        except Exception as e:
            messages.append(f"An unexpected error occurred: {e}")
    try:
        ticker = yf.Ticker(ticker_symbol)
        # Retrieve financial statements
        income_statement = ticker.financials.T

        # Select the latest year's data
        latest_year_data = income_statement.iloc[-1]

        # Calculate earnings per share
        latest_net_income = latest_year_data['Net Income']
        latest_common_stock = ticker.info.get('sharesOutstanding', None)
        latest_eps = latest_net_income / latest_common_stock if latest_common_stock else "N/A"

        # Calculate key ratios
        gross_margin = (latest_year_data['Gross Profit'] / latest_year_data['Total Revenue']) * 100
        operating_margin = (latest_year_data['Operating Income'] / latest_year_data['Total Revenue']) * 100
        net_margin = (latest_year_data['Net Income'] / latest_year_data['Total Revenue']) * 100

        # Create a DataFrame for displaying key ratios
        key_ratios_data = {
            'Gross Margin': [gross_margin],
            'Operating Margin': [operating_margin],
            'Net Margin': [net_margin]
        }
        key_ratios_df = pd.DataFrame(key_ratios_data)

        context = {'stock_info': ticker.info.items(),
                   'latest_year_data': latest_year_data,
                   'latest_eps': latest_eps,
                   'key_ratios_df': key_ratios_df,
                   'plot_div': plot_div,
                   'stock_id': stock_id,
                   'button_text': button_text
                   }
    except Exception as e:
        messages.append(f"An unexpected error occurred: {e}")
    if len(messages) > 0:
        context['messages'] = messages
    return render(request, 'chart.html', context=context)


@login_required(login_url='signin')
def follow_chart(request, pk):
    username = request.user.username
    stock = Stock.objects.get(id=pk)

    follow_filter = FollowChart.objects.filter(chart_id=stock.id, username=username).first()
    if follow_filter == None:
        new_follow = FollowChart.objects.create(chart_id=stock.id, username=username)
        new_follow.save()
        stock.follows += 1
        stock.save()
    else:
        follow_filter.delete()
        stock.follows -= 1
        stock.save()

    return redirect('/')


def search(request):
    plot_div = None
    stock = ""
    messages = []

    if request.method == "POST":
        stock = request.POST["stock"]

        try:
            # Fetch stock data
            stock_data = yf.download(stock, start='2023-01-01', end=datetime.today().strftime('%Y-%m-%d'), interval='1d')

            # Create the candlestick chart
            fig = go.Figure(data=[go.Candlestick(x=stock_data.index,
                                                 open=stock_data['Open'],
                                                 high=stock_data['High'],
                                                 low=stock_data['Low'],
                                                 close=stock_data['Close'])])

            # Update layout
            fig.update_layout(title=f'{stock}/USD',
                              xaxis_rangeslider_visible=False)
            if not Stock.objects.filter(ticker=stock).exists():
                new_stock = Stock.objects.create(ticker=stock)
                new_stock.save()
                stock_id = new_stock.id
            else:
                old_stock = Stock.objects.get(ticker=stock)
                stock_id = old_stock.id

            plot_div = plot(fig, output_type='div')
        except Exception as e:
            messages.append(f"An unexpected error occurred: {e}")
    context = {'plot_div': plot_div,
               'stock': stock,
               'messages': messages,
               'stock_id': stock_id
               }
    return render(request, 'search.html', context=context)


