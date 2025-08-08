from deep_translator import GoogleTranslator


def define_str_language(s: str):
    eng_counter = 0
    ru_counter = 0
    for symb in s:
        if 1072 <= ord(symb) <= 1103:
            ru_counter += 1
        elif 97 <= ord(symb) <= 122:
            eng_counter += 1

    if ru_counter > eng_counter:
        return 'ru'
    return 'eng'

print(define_str_language("Привет, как дела"))
print(GoogleTranslator(source='ru', target='en').translate('Привет, как дела'))
