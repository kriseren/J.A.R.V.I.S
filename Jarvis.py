import asyncio
import datetime
import json

import pyttsx3
import speech_recognition as sr

import entertainment.f1.next_gp as next_gp
import iot.meross.meross_controller
from sentences.sentence_generator import SentenceType, generate_sentence
from storage.dtos.owner import Owner

# Inicializar el motor TTS (Texto a Voz)
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)  # El id controla la voz.


def load_owner_from_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as json_file:
            owner_data = json.load(json_file)
            return Owner(owner_data["name"], owner_data["age"], owner_data["title"])
    except FileNotFoundError:
        print("El archivo JSON del propietario no existe.")
        return None


def save_owner_to_json(filename, owner):
    try:
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(owner.__dict__, json_file, ensure_ascii=False)
    except FileNotFoundError:
        print("El archivo JSON del propietario no existe.")


def say(text, rate=220):
    # Imprimir por pantalla el texto.
    print(f"[J] {text}")
    # Utilizar el motor TTS para decir el texto
    engine.setProperty("rate", rate)  # Ajustar la velocidad de reproducción
    engine.say(text)
    engine.runAndWait()



def transcribe_audio(timeout=2):
    # Crear un objeto reconocedor de voz
    recognizer = sr.Recognizer()

    # Usar el micrófono como fuente de audio
    with sr.Microphone() as source:
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


async def control_plug(action):
    # Ejecutar la función main del script de control del enchufe Meross con el argumento apropiado
    await iot.meross.meross_controller.main(action, None, None)


def generate_response(input_text, owner):
    # Selecciona una frase de no entendido aleatoria
    return generate_sentence(owner, SentenceType.NOT_UNDERSTOOD)


def update_owner_info_interactive(owner):
    try:
        say("¿Cuál es su nombre?")
        name = transcribe_audio()
        owner.name = name
        print(f"[{owner.name.upper()[0]}] " + name)

        say("¿Cuántos años tiene?")
        age = int(transcribe_audio())
        owner.age = age
        print(f"[{owner.name.upper()[0]}] " + age)

        say("¿Qué título le gustaría que usase? Por ejemplo: señor, señora, maestro, maestra...")
        title = transcribe_audio()
        owner.title = title
        print(f"[{owner.name.upper()[0]}] " + title)

        save_owner_to_json("storage/json/owner.json", owner)
        say("Información del propietario actualizada con éxito.")
        return owner
    except ValueError:
        say("No pude entender la información del propietario.")


async def main():
    try:

        # Obtener los datos del propietario.
        owner = load_owner_from_json("storage/json/owner.json")

        # Bucle infinito para mantener el programa escuchando continuamente
        while True:
            # Escuchar continuamente hasta que se detecte la palabra clave "Jarvis"
            print("Escuchando...")
            while True:
                trigger_word = transcribe_audio()
                if trigger_word and "jarvis" in trigger_word:
                    break

            # Una vez que se detecta "Jarvis", escuchar el comando después de "Jarvis"
            say(generate_sentence(owner, SentenceType.GREETING))  # Selecciona una frase de saludo aleatoria
            command = transcribe_audio()
            print(f"[{owner.name.upper()[0]}] " + command)

            # Analizar el comando para determinar si se debe encender el enchufe.
            if "inicia" in command and "protocolo" in command and "buenos días" in command:
                say(f"¡Claro {owner.title}! Iniciando el protocolo buenos días...")
                await control_plug("on")
            elif (
                    "inicia" in command
                    and "protocolo" in command
                    and "buenas noches" in command
            ):
                say(f"¡Por supuesto {owner.title}! Protocolo buenas noches iniciado...")
                await control_plug("off")
            elif "hora" in command and "es" in command:
                # Obtener la hora actual
                current_time = datetime.datetime.now().time()
                # Convertir la hora a un formato legible
                current_time_str = current_time.strftime("%I:%M %p")
                # Decir la hora actual utilizando J.A.R.V.I.S.
                say("Son las " + current_time_str + ", " + owner.title)
            elif (
                    "cuándo" in command and "gran premio" in command and "fórmula 1" in command
            ):
                message = next_gp.get_next_gp_message()
                say(message)

            elif "es" in command and "mi" in command and "nombre" in command:
                say(f"Su nombre es {owner.name}")
            elif "actualizar" in command and "datos" in command and "mis" in command or "propietario" in command:
                owner = update_owner_info_interactive(owner)
            elif "apágate" in command or "apagar" in command:
                # Selecciona una frase de despedida aleatoria
                farewell_response = generate_sentence(owner, SentenceType.FAREWELL)
                say(farewell_response)
                break
            else:
                # Llama a la función para generar una respuesta
                response = generate_response(command, owner)
                say(response)
    except Exception as ex:
        say(f"Lamentablemente he sufrido el siguiente error: {ex}")


if __name__ == "__main__":
    asyncio.run(main())
