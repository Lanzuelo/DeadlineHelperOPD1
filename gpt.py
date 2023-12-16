import g4f
from settings import settings_ai
import openai

openai.api_key = settings_ai['Token']


def gpt(prompt: str):
    completion = openai.api_key.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content


def gpt3_free(prompt: str):
    '''
    Функиция обрабатывает запрос с помощью свободного сервера "GPT 3.5-turbo".

    Args:
        prompt (str): Запрос к серверу "GPT 3.5-turbo".

    Returns:
        str: Ответ с сервера "GPT 3.5-turbo".

    Extra:
        Если нет свободных серверов, вернут ошибку "Сервер не отвечает".
    '''
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        result = ''
        for message in response:
            result += message
        return result

    except RuntimeError:
        return 'Сервер не отвечает'


def gpt4_free(prompt: str):
    '''
    Функиция обрабатывает запрос с помощью свободного сервера "GPT 4".

    Args:
        prompt (str): Запрос к серверу "GPT 4".

    Returns:
        str: Ответ с сервера "GPT 4".

    Extra:
        Если нет свободных серверов, вернут ошибку "Сервер не отвечает".
    '''
    try:
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4,
            messages=[{"role": "user", "content": prompt}],
        )

        print('gpt_4')
        return response

    except RuntimeError:
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        result = ''
        for message in response:
            result += message

        print('gpt_3')
        return result

    except:
        return 'Сервер не отвечает'