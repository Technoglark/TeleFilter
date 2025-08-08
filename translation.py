import pandas as pd
from transformers import MarianMTModel, MarianTokenizer


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Переводит текст с одного языка на другой с помощью моделей MarianMT.

    Args:
        text (str): Текст для перевода.
        source_lang (str): Исходный язык (например, 'en' для английского).
        target_lang (str): Целевой язык (например, 'ru' для русского).

    Returns:
        str: Переведенный текст.
    """
    model_name = f'Helsinki-NLP/opus-mt-{source_lang}-{target_lang}'
    try:
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
    except OSError:
        return f"Ошибка: Модель для пары языков {source_lang}-{target_lang} не найдена. Проверьте доступные модели на Hugging Face Hub."
    tokenized_text = tokenizer(text, return_tensors="pt", padding=True)

    translated_tokens = model.generate(**tokenized_text)
    translated_text = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]

    return translated_text


def create_translated_dataset(filename):
    eng_dataset = pd.read_csv(filename)[:10]
    categories = eng_dataset.Category
    messages = eng_dataset.Message
    ru_messages = []
    for i, message in enumerate(messages):
        print(f"iteration {i}")
        ru_messages.append(translate_text(message, 'en', 'ru'))
    ru_messages_df = pd.DataFrame(ru_messages)

    dataset = pd.concat([categories.reset_index(drop=True), ru_messages_df.reset_index(drop=True)], axis=1)
    dataset.to_csv('spam_ru.csv')

create_translated_dataset('spam.csv')
