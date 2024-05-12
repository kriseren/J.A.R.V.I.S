import random

import sentences.farewell_responses as farewell_responses
import sentences.greetings as greetings
import sentences.not_understood_responses as not_understood_responses


class SentenceType:
    GREETING = "greeting"
    FAREWELL = "farewell"
    NOT_UNDERSTOOD = "not_understood"


def generate_sentence(owner, sentence_type):
    if sentence_type == SentenceType.GREETING:
        return generate_greeting(owner)
    elif sentence_type == SentenceType.FAREWELL:
        return generate_farewell(owner)
    elif sentence_type == SentenceType.NOT_UNDERSTOOD:
        return generate_not_understood(owner)
    else:
        return "Tipo de frase no válido."


def generate_greeting(owner):
    greeting = random.choice(greetings.greetings)
    return greeting.format(title=owner.title, name=owner.name)


def generate_farewell(owner):
    farewell_response = random.choice(farewell_responses.farewell_responses)
    return farewell_response.format(title=owner.title, name=owner.name)


def generate_not_understood(owner):
    not_understood_response = random.choice(not_understood_responses.not_understood_responses)
    return not_understood_response.format(title=owner.title, name=owner.name)
