import asyncio
import datetime
import json
import random

import pyttsx3
import speech_recognition as sr

import entertainment.f1.next_gp as next_gp
import iot.meross.meross_controller
import sentences.farewell_responses as farewell_responses
import sentences.greetings as greetings
import sentences.not_understood_responses as not_understood_responses
from storage.dtos.owner import Owner

# Inicializar el motor TTS (Texto a Voz)
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)  # El id controla la voz.


def load_owner_from_json(filename):
    try:
        with open(filename, "r") as json_file:
            owner_data = json.load(json_file)
            return Owner(owner_data["name"], owner_data["age"])
    except FileNotFoundError:
        print("El archivo JSON del dueño no existe.")
        return None


def save_owner_to_json(filename, owner):
    try:
        with open(filename, "w") as json_file:
            json.dump(owner.__dict__, json_file)
            print("Información del propietario actualizada con éxito.")
    except FileNotFoundError:
        print("El archivo JSON del dueño no existe.")


def say(text):
    # Imprimir por pantalla el texto.
    print(text)
    # Utilizar el motor TTS para decir el texto
    engine.say(text)
    engine.runAndWait()


def transcribe_audio(timeout=2):
    # Crear un objeto reconocedor de voz
    recognizer = sr.Recognizer()

    # Usar el micrófono como fuente de audio
    with sr.Microphone() as source:
        print("Escuchando...")
        try:
            # Escuchar el audio del micrófono con un tiempo de espera máximo definido
            audio = recognizer.listen(source, timeout=timeout)
        except sr.WaitTimeoutError:
            return ""

    try:
        # Transcribir el audio utilizando el servicio de Google
        text = recognizer.recognize_google(audio, language="es-ES")
        return text.lower()
    except sr.UnknownValueError:
        print("No se pudo entender el audio")
    except sr.RequestError as e:
        print("Error al solicitar la transcripción; {0}".format(e))


async def controlar_enchufe(action):
    # Ejecutar la función main del script de control del enchufe Meross con el argumento apropiado
    await iot.meross.meross_controller.main(action, None, None)


def generate_response(input_text):
    # Selecciona una frase de no entendido aleatoria
    return random.choice(not_understood_responses.not_understood_responses)


def update_owner_info_interactive(owner):
    try:
        say("¿Cuál es tu nombre?")
        name = transcribe_audio()
        owner.name = name

        say("¿Cuántos años tienes?")
        age = int(transcribe_audio())
        owner.age = age

        save_owner_to_json("storage/json/owner.json", owner)
        say("Información del propietario actualizada con éxito.")
    except ValueError:
        say("No pude entender la información del propietario. ¿Podrías repetirla?")


async def main():
    # Obtener los datos del dueño.
    owner = load_owner_from_json("storage/json/owner.json")

    # Bucle infinito para mantener el programa escuchando continuamente
    while True:
        # Escuchar continuamente hasta que se detecte la palabra clave "Jarvis"
        while True:
            trigger_word = transcribe_audio()
            if trigger_word and ("jarvis") in trigger_word:
                break

        # Una vez que se detecta "Jarvis", escuchar el comando después de "Jarvis"
        say(random.choice(greetings.greetings).format(owner.name))  # Selecciona una frase de saludo aleatoria
        command = transcribe_audio()
        print("Comando detectado: " + command)  # Decir el comando detectado

        # Analizar el comando para determinar si se debe encender el enchufe.
        if "inicia" in command and "protocolo" in command and "buenos días" in command:
            say("¡Claro señor! Iniciando el protocolo buenos días...")
            await controlar_enchufe("on")
        elif (
                "inicia" in command
                and "protocolo" in command
                and "buenas noches" in command
        ):
            say("¡Por supuesto señor! Protocolo buenas noches iniciado...")
            await controlar_enchufe("off")
        elif "hora" in command and "es" in command:
            # Obtener la hora actual
            current_time = datetime.datetime.now().time()
            # Convertir la hora a un formato legible
            current_time_str = current_time.strftime("%I:%M %p")
            # Decir la hora actual utilizando J.A.R.V.I.S.
            say("Son las " + current_time_str + ", señor")
        elif (
                "cuándo" in command and "gran premio" in command and "fórmula 1" in command
        ):
            message = next_gp.get_next_gp_message()
            say(message)

        elif "es" in command and "mi" in command and "nombre" in command:
            say("Tu nombre es " + owner.name)
        elif "actualiza" in command and "propietario" in command:
            update_owner_info_interactive(owner)
        elif "apágate" in command:
            # Selecciona una frase de despedida aleatoria
            say(random.choice(farewell_responses.farewell_responses).format(owner.name))
            break
        else:
            # Llama a la función para generar una respuesta
            response = generate_response(command).format(owner.name)
            say(response)


if __name__ == "__main__":
    asyncio.run(main())
