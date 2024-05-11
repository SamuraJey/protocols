#!/usr/bin/env python
import cgi # depricated :crying_face:

# Получаем данные из query params
params = cgi.FieldStorage()

# Выводим заголовок Content-Type
print("Content-Type: text/html")
print()

# Выводим полученные данные
print("<h1>Query Params:</h1>")
print("<ul>")
for param in params:
    print(f"<li>{param}: {params[param].value}</li>")
print("</ul>")