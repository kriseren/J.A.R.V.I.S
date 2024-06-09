import random

from llamaapi import LlamaAPI

import auth.auth
import sentences.farewell_responses as farewell_responses
import sentences.greetings as greetings
import sentences.not_understood_responses as not_understood_responses


class SentenceType:
    GREETING = "greeting"
    FAREWELL = "farewell"
    NOT_UNDERSTOOD = "not_understood"


def generate_sentence(owner, sentence_type):
    """
    Genera una frase basada en el tipo de frase y la información del propietario.

    Args:
        owner (object): Información del propietario.
        sentence_type (str): Tipo de frase (greeting, farewell, not_understood).

    Returns:
        str: Frase generada.
    """
    if sentence_type == SentenceType.GREETING:
        return generate_greeting(owner)
    elif sentence_type == SentenceType.FAREWELL:
        return generate_farewell(owner)
    elif sentence_type == SentenceType.NOT_UNDERSTOOD:
        return generate_not_understood(owner)
    else:
        return "Tipo de frase no válido."


def generate_greeting(owner):
    """
    Genera una frase de saludo.

    Args:
        owner (object): Información del propietario.

    Returns:
        str: Frase de saludo.
    """
    greeting = random.choice(greetings.greetings)
    return greeting.format(title=owner.title, name=owner.name)


def generate_farewell(owner):
    """
    Genera una frase de despedida.

    Args:
        owner (object): Información del propietario.

    Returns:
        str: Frase de despedida.
    """
    farewell_response = random.choice(farewell_responses.farewell_responses)
    return farewell_response.format(title=owner.title, name=owner.name)


def generate_not_understood(owner):
    """
    Genera una frase de no entendimiento.

    Args:
        owner (object): Información del propietario.

    Returns:
        str: Frase de no entendimiento.
    """
    not_understood_response = random.choice(not_understood_responses.not_understood_responses)
    return not_understood_response.format(title=owner.title, name=owner.name)


def generate_ai_response(input_text):
    """
    Genera una respuesta de IA utilizando la API de Llama.

    Args:
        input_text (str): Texto de entrada para la IA.

    Returns:
        str: Respuesta generada por la IA.
    """
    llama = LlamaAPI(auth.auth.LLAMA_API_TOKEN)

    # JSON de solicitud a la API
    api_request_json = {
        "model": "llama3-70b",
        "messages": [
            {"role": "system", "content": "Responde de manera breve y concisa."},
            {"role": "user", "content": input_text},
        ],
        "max_tokens": 50  # Limitar el número de tokens para respuestas más cortas
    }

    # Realizar la solicitud y manejar la respuesta
    response = llama.run(api_request_json)

    # Extraer el contenido de la respuesta
    response_content = response.json().get('choices', [{}])[0].get('message', {}).get('content',
                                                                                      "No se pudo generar una respuesta.")

    return response_content
