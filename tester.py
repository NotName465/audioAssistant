def num_to_words_ru(num):
    """Преобразует число в слова на русском"""
    if num == 0:
        return "ноль"

    units = {
        1: "один", 2: "два", 3: "три", 4: "четыре", 5: "пять",
        6: "шесть", 7: "семь", 8: "восемь", 9: "девять"
    }

    teens = {
        10: "десять", 11: "одиннадцать", 12: "двенадцать", 13: "тринадцать",
        14: "четырнадцать", 15: "пятнадцать", 16: "шестнадцать",
        17: "семнадцать", 18: "восемнадцать", 19: "девятнадцать"
    }

    tens = {
        20: "двадцать", 30: "тридцать", 40: "сорок", 50: "пятьдесят",
        60: "шестьдесят", 70: "семьдесят", 80: "восемьдесят", 90: "девяносто"
    }

    hundreds = {
        100: "сто", 200: "двести", 300: "триста", 400: "четыреста",
        500: "пятьсот", 600: "шестьсот", 700: "семьсот", 800: "восемьсот",
        900: "девятьсот"
    }

    if num in units:
        return units[num]
    elif num in teens:
        return teens[num]
    elif num in tens:
        return tens[num]
    elif num in hundreds:
        return hundreds[num]

    result = []

    if num >= 1000:
        thou = num // 1000
        if thou == 1:
            result.append("тысяча")
        elif thou == 2:
            result.append("две тысячи")
        elif thou == 3:
            result.append("три тысячи")
        elif thou == 4:
            result.append("четыре тысячи")
        elif thou == 5:
            result.append("пять тысяч")
        elif thou == 6:
            result.append("шесть тысяч")
        elif thou == 7:
            result.append("семь тысяч")
        elif thou == 8:
            result.append("восемь тысяч")
        else:
            return f"{num_to_words_ru(thou)} тысяч"
        num %= 1000

    if num >= 100:
        hundreds_part = (num // 100) * 100
        if hundreds_part in hundreds:
            result.append(hundreds[hundreds_part])
        num %= 100

    if num >= 20:
        tens_part = (num // 10) * 10
        if tens_part in tens:
            result.append(tens[tens_part])
        num %= 10

    if num >= 10:
        if num in teens:
            result.append(teens[num])
        num = 0

    if num > 0:
        result.append(units[num])

    return " ".join(result)


# Создаем полный словарь всех чисел от 1 до 8000
word_to_digit = {}

for i in range(1, 8001):
    word = num_to_words_ru(i)
    word_to_digit[word] = i

    # Добавляем варианты без пробелов
    without_spaces = word.replace(" ", "")
    if without_spaces != word:
        word_to_digit[without_spaces] = i

    # Добавляем варианты с дефисами
    with_hyphen = word.replace(" ", "-")
    if with_hyphen != word:
        word_to_digit[with_hyphen] = i


def word_to_number(word):
    """Преобразует слово в число"""
    word = word.strip().lower()

    # Прямой поиск в словаре
    if word in word_to_digit:
        return word_to_digit[word]

    return None


def extract_number_from_text(text_list):
    """Извлекает число из списка слов"""
    # Очищаем от слов "пикселей", "пикселя", "пиксель"
    clean_words = []
    for word in text_list:
        if isinstance(word, str):
            clean_word = word.lower().replace("пикселей", "").replace("пикселя", "").replace("пиксель", "").strip()
            if clean_word:
                clean_words.append(clean_word)

    # Пробуем найти числа разной длины (от 4 до 1 слов)
    for start in range(len(clean_words)):
        for length in range(min(4, len(clean_words) - start), 0, -1):  # От 4 до 1
            phrase = " ".join(clean_words[start:start + length])
            number = word_to_number(phrase)

            if number is not None:
                return number

    return 100


# Тестирование
if __name__ == "__main__":
    test_cases = [
        (["сто", "пятьдесят", "два"], 152),
        (["двести", "пятьдесят"], 250),
        (["триста", "сорок", "семь"], 347),
        (["пятьсот", "восемьдесят"], 580),
        (["шестьсот"], 600),
        (["семьсот", "девяносто", "три"], 793),
        (["тысяча"], 1000),
        (["пять", "тысяч"], 5000),
        (["восемь", "тысяч"], 8000),
        (["сто", "двадцать", "три"], 123),
        (["двадцать", "пять"], 25),
        (["сорок", "восемь"], 48),
    ]

    print("Тестирование распознавания чисел:")
    print("=" * 50)

    all_passed = True
    for words, expected in test_cases:
        result = extract_number_from_text(words)
        status = "✅" if result == expected else "❌"
        print(f"{status} {' '.join(words):<30} -> {result} (ожидается: {expected})")
        if result != expected:
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ!")

    # Дополнительный тест с пикселями
    print("\nТест с пикселями:")
    test_with_pixels = ["перемести", "на", "сто", "пятьдесят", "два", "пикселя"]
    result = extract_number_from_text(test_with_pixels)
    print(f"{' '.join(test_with_pixels)} -> {result} (ожидается: 152)")