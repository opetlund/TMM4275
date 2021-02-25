import requests


url = 'http://127.0.0.1:1234/orderChair'
x = requests.get('url', data= 'a= &b= & c= & d= ')

print(x.text)