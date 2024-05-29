import asyncio
import datetime
import os
import re

import entertainment.f1.next_gp as next_gp
import iot.meross.meross_controller
from entertainment.matavise.matavise import get_random_death
from sentences.sentence_generator import SentenceType, generate_sentence
from storage.implementations.config_manager import load_config_from_json, update_config_interactive
from storage.implementations.owner_manager import load_owner_from_json, update_owner_info_interactive, get_owner_info
from voice.voice_manager import say, transcribe_audio

# Definir el nombre predeterminado de la palabra clave
DEFAULT_WAKE_WORD = "Jarvis"

# Lista para almacenar tareas de recordatorio
reminder_tasks = []


async def control_plug(action):
    # Ejecutar la función main del script de control del enchufe Meross con el argumento apropiado
    await iot.meross.meross_controller.main(action, None, None)


def generate_response(input_text, owner):
    # Selecciona una frase de no entendido aleatoria
    return generate_sentence(owner, SentenceType.NOT_UNDERSTOOD)


async def restart_computer():
    # Despedirse antes de reiniciar
    say("Hasta luego, nos vemos después del reinicio.")
    # Reiniciar el equipo
    os.system("shutdown /r /t 1")


async def remind(task, delay):
    print("Dentro de remind")
    await asyncio.sleep(delay)
    say(f"Recuerda: {task}")


def parse_reminder_command(command):
    match = re.search(r"recuérdame que (.+) en (\d+) (segundos|minutos|horas)", command)
    if match:
        task = match.group(1)
        amount = int(match.group(2))
        unit = match.group(3)
        if unit == "segundos":
            delay = amount
        elif unit == "minutos":
            delay = amount * 60
        elif unit == "horas":
            delay = amount * 3600
        else:
            delay = 0
        return task, delay
    return None, None


async def main():
    try:
        # Cargar la configuración del archivo JSON
        config = load_config_from_json("storage/json/config.json")
        # Obtener el nombre de la palabra clave desde la configuración o usar el predeterminado
        wake_word = config.wake_word if config else DEFAULT_WAKE_WORD

        # Obtener los datos del propietario.
        owner = load_owner_from_json("storage/json/owner.json")

        # Bucle infinito para mantener el programa escuchando continuamente
        while True:
            # Escuchar continuamente hasta que se detecte la palabra clave
            print("Escuchando...")
            try:
                while True:
                    trigger_word = transcribe_audio()
                    if trigger_word and wake_word.lower() in trigger_word.lower():
                        break
            except Exception as ex:
                say(f"Error al escuchar: {ex}")
                continue

            # Una vez que se detecta la palabra clave, escuchar el comando después de la palabra clave
            say(generate_sentence(owner, SentenceType.GREETING))  # Selecciona una frase de saludo aleatoria
            command = transcribe_audio()
            print(f"[{owner.name.upper()[0]}] " + command)

            # Analizar el comando para determinar la acción a tomar.
            if re.search(r"(inicia|activa).*(protocolo).*buenos días", command):
                say(f"¡Claro {owner.title}! Iniciando el protocolo buenos días...")
                await control_plug("on")
            elif re.search(r"(inicia|activa).*(protocolo).*buenas noches", command):
                say(f"¡Por supuesto {owner.title}! Protocolo buenas noches iniciado...")
                await control_plug("off")
            elif re.search(r"(qué hora|hora es|dime la hora)", command):
                # Obtener la hora actual
                current_time = datetime.datetime.now().time()
                # Convertir la hora a un formato legible
                current_time_str = current_time.strftime("%I:%M %p")
                # Decir la hora actual utilizando el nombre del propietario
                say("Son las " + current_time_str + ", " + owner.title)
            elif re.search(r"(cuándo|próximo|siguiente).*gran premio.*fórmula 1", command):
                message = next_gp.get_next_gp_message()
                say(message)
            elif re.search(r"mi nombre|cómo me llamo", command):
                say(f"Su nombre es {owner.name}")
            elif re.search(r"(actualiza|modifica).*datos.*propietario", command):
                owner = update_owner_info_interactive(owner)
            elif re.search(r"(apágate|apagar|detente)", command):
                # Selecciona una frase de despedida aleatoria
                farewell_response = generate_sentence(owner, SentenceType.FAREWELL)
                say(farewell_response)
                break
            elif re.search(r"(quién|cómo|cuál).*propietario|quién soy", command):
                owner_info = get_owner_info(owner)
                say(owner_info)
            elif re.search(r"(dime|decir|cuéntame).*muerte.*vise|matavise|vice|matavice", command):
                death = get_random_death()
                say(death)
            elif re.search(r"(reinicia|reiniciar).*ordenador|equipo|sistema", command):
                await restart_computer()
            elif re.search(r"(cambiar|modificar|quiero cambiar).*(palabra.*clave|clave.*palabra|clave|palabra)",
                           command):
                config = update_config_interactive(config)
                if config:
                    wake_word = config.wake_word
                    say(f"La nueva palabra clave es {wake_word}.")
            elif re.search(r"recuérdame que", command):
                task, delay = parse_reminder_command(command)
                if task and delay:
                    say(f"Te recordaré {task} en {delay} segundos.")
                    reminder_task = asyncio.create_task(remind(task, delay))
                    reminder_tasks.append(reminder_task)
                else:
                    say("No pude entender el tiempo especificado para el recordatorio.")
            else:
                # Llama a la función para generar una respuesta
                response = generate_response(command, owner)
                say(response)

            # Asegurarse de que se ejecuten las tareas de recordatorio
            await asyncio.gather(*reminder_tasks)
    except Exception as ex:
        say(f"Lamentablemente he sufrido el siguiente error: {ex}")


if __name__ == "__main__":
    asyncio.run(main())
