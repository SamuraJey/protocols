def base64_decode(base64_string):
    BASE64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    PADDING_CHAR = "="

    # Удаляем символы заполнения в конце строки base64
    while base64_string[-1] == PADDING_CHAR:
        base64_string = base64_string[:-1]

    # Конвертируем строку base64 в строку битов
    # Итерируемся по строке base64, находим индекс символа в строке
    # BASE64_CHARS и записываем его в строку битов
    bit_string = ""
    for char in base64_string:
        if char in BASE64_CHARS:
            bit_string += bin(BASE64_CHARS.index(char))[2:].zfill(6)

    # Конвертируем строку битов в строку байтов
    # Итерируемся по строке с битами, с шагом 8 бит и конвертируем их в символ
    byte_string = ""
    for i in range(0, len(bit_string) - 7, 8): # Это исключит лишнюю итерацию
        byte_string += chr(int(bit_string[i:i+8], 2))

    return byte_string


base64_string = "IkluIEMrKyBpdCdzIGhhcmRlciB0byBzaG9vdCB5b3Vyc2VsZiBpbiB0aGUg\
Zm9vdCwgYnV0IHdoZW4geW91IGRvLCB5b3UgYmxvdyBvZmYgeW91ciB3aG9sZSBsZWcuICIgLS0gQ\
mphcm5lIFN0cm91c3RydXA=="
decoded_string = base64_decode(base64_string)
print(decoded_string)
