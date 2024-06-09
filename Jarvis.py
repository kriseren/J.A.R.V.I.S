import argparse
import asyncio
import datetime
import os
import re

import entertainment.f1.next_gp as next_gp
import iot.meross.meross_controller
from entertainment.matavise.matavise import get_random_death
from entertainment.spotify.spotify_manager import play_pause, next_track, previous_track
from sentences.sentence_generator import SentenceType, generate_sentence, generate_ai_response
from storage.implementations.config_manager import load_config_from_json, update_config_interactive
from storage.implementations.owner_manager import load_owner_from_json, update_owner_info_interactive, get_owner_info
from voice.voice_manager import say, transcribe_audio, get_command_input

# Definir el nombre predeterminado de la palabra clave
DEFAULT_WAKE_WORD = "Jarvis"

# Lista para almacenar tareas de recordatorio
reminder_tasks = []


async def control_plug(action):
    """Controla el enchufe Meross."""
    await iot.meross.meross_controller.main(action, None, None)


def generate_response(owner):
    """Genera una respuesta de no entendido."""
    return generate_sentence(owner, SentenceType.NOT_UNDERSTOOD)


async def restart_computer():
    """Reinicia el ordenador con confirmación."""
    say("¿Está seguro que desea reiniciar el sistema? Diga 'sí' para confirmar o 'no' para cancelar.")
    confirmation = transcribe_audio()
    if confirmation.lower() == "sí":
        say("Reiniciando el sistema.")
        os.system("shutdown /r /t 1")
    else:
        say("Reinicio cancelado.")


async def shutdown_computer():
    """Apaga el ordenador con confirmación."""
    say("¿Está seguro que desea apagar el sistema? Diga 'sí' para confirmar o 'no' para cancelar.")
    confirmation = transcribe_audio()
    if confirmation.lower() == "si" or confirmation.lower() == "sí":
        say("Apagando el sistema.")
        os.system("shutdown /s /t 1")
    else:
        say("Apagado cancelado.")


async def remind(task, delay):
    """Crea una tarea de recordatorio."""
    await asyncio.sleep(delay)
    say(f"Recuerda: {task}")


def parse_reminder_command(command):
    """Parsea el comando de recordatorio para extraer la tarea y el tiempo."""
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


async def handle_command(command, owner, config, input_mode):
    """Maneja los comandos recibidos después de detectar la palabra clave."""
    if re.search(r"(inicia|activa).*(protocolo).*buenos días", command):
        say(f"¡Claro {owner.title}! Iniciando el protocolo buenos días...")
        await control_plug("on")
    elif re.search(r"(inicia|activa).*(protocolo).*buenas noches", command):
        say(f"¡Por supuesto {owner.title}! Protocolo buenas noches iniciado...")
        await control_plug("off")
    elif re.search(r"(qué hora|hora es|dime la hora)", command):
        current_time = datetime.datetime.now().time()
        current_time_str = current_time.strftime("%I:%M %p")
        say("Son las " + current_time_str + ", " + owner.title)
    elif re.search(r"(cuándo|próximo|siguiente).*gran premio.*fórmula 1", command):
        message = next_gp.get_next_gp_message()
        say(message)
    elif re.search(r"mi nombre|cómo me llamo", command):
        say(f"Su nombre es {owner.name}")
    elif re.search(r"(actualiza|modifica).*datos.*propietario", command):
        owner = update_owner_info_interactive(owner, input_mode)
    elif re.search(r"(apágate|apagar|detente)", command):
        farewell_response = generate_sentence(owner, SentenceType.FAREWELL)
        say(farewell_response)
        return False
    elif re.search(r"(quién|cómo|cuál).*propietario|quién soy", command):
        owner_info = get_owner_info(owner)
        say(owner_info)
    elif re.search(r"(dime|decir|cuéntame).*muerte.*vise|matavise|vice|matavice", command):
        death = get_random_death()
        say(death)
    elif re.search(r"(reinicia|reiniciar).*ordenador|equipo|sistema", command):
        await restart_computer()
    elif re.search(r"(apaga|apagar).*ordenador|equipo|sistema", command):
        await shutdown_computer()
    elif re.search(r"(actualizar|cambiar|modificar|quiero cambiar).*(palabra.*clave|clave.*palabra|clave|palabra)",
                   command):
        config = update_config_interactive(config, input_mode)
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
    elif re.search(r"(reproducir|pausa|pausar|reproduce).*música", command):
        play_pause()
        say("Control de reproducción de música ejecutado.")
    elif re.search(r"siguiente.*canción", command):
        next_track()
        say("Pasando a la siguiente canción.")
    elif re.search(r"(canción anterior|volver|retroceder).*canción", command):
        previous_track()
        say("Volviendo a la canción anterior.")
    else:
        if command and config.use_ai:
            response = generate_ai_response(command)
        else:
            response = generate_response(owner)
        say(response)
    return True


async def main(input_mode):
    """Función principal del asistente virtual."""
    try:
        # Cargar la configuración del archivo JSON.
        config = load_config_from_json("storage/json/config.json")
        wake_word = config.wake_word if config else DEFAULT_WAKE_WORD

        # Obtener los datos del propietario.
        owner = load_owner_from_json("storage/json/owner.json")

        # Bucle infinito para mantener el programa escuchando continuamente.
        while True:
            print("Escuchando...")
            try:
                while True:
                    trigger_word = get_command_input(input_mode)
                    if trigger_word and wake_word.lower() in trigger_word.lower():
                        break
            except Exception as ex:
                say(f"Error al escuchar: {ex}")
                continue

            say(generate_sentence(owner, SentenceType.GREETING))
            command = get_command_input(input_mode)
            print(f"[{owner.name.upper()[0]}] " + command)

            # Manejar el comando recibido
            if not await handle_command(command, owner, config, input_mode):
                break

            # Eliminar las tareas de recordatorio completadas
            reminder_tasks[:] = [task for task in reminder_tasks if not task.done()]

    except Exception as ex:
        say(f"Lamentablemente he sufrido el siguiente error: {ex}")


def parse_args():
    """Parsea los argumentos de la línea de comandos."""
    parser = argparse.ArgumentParser(description="Asistente Virtual J.A.R.V.I.S")
    parser.add_argument(
        "--input-mode",
        choices=["voice", "text"],
        default="voice",
        help="Modo de entrada de comandos (voice o text)."
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args.input_mode))
