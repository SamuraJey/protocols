# Portscan

## Формулировка
Написать сканер TCP- и UDP-портов удалённого компьютера.
Вход: адрес хоста и диапазон портов
Выход: итоговая оценка складывается как сумма:
- [1-2 балла] список открытых TCP-портов,
- [1-4 балла] список открытых UDP-портов,
- [1-3 балла] многопоточность,
- [1-6 балла] распознать прикладной протокол по сигнатуре (NTP/DNS/SMTP/POP3/IMAP/HTTP).

## Формат ввода-вывода
### Параметры:
- `-t` - сканировать tcp
- `-u` - сканировать udp
- `-p N1 N2, --ports N1 N2` - диапазон портов

### Вывод:
В одной строке информация об одном открытом порте (через пробел):
- TCP 80 HTTP
- UDP 128
- UDP 123 SNTP

Если протокол не распознали, то пишем только TCP/UDP и номер порта.
Если нужно больше прав при запуске, то стоит вежливо об этом сказать, а не громко падать.