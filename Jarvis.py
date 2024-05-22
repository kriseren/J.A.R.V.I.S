import asyncio
import datetime
import os

import entertainment.f1.next_gp as next_gp
import iot.meross.meross_controller
from entertainment.matavise.matavise import get_random_death
from sentences.sentence_generator import SentenceType, generate_sentence
from storage.implementations.config_manager import load_config_from_json, update_config_interactive
from storage.implementations.owner_manager import load_owner_from_json, update_owner_info_interactive, get_owner_info
from voice.voice_manager import say, transcribe_audio

# Definir el nombre predeterminado de la palabra clave
DEFAULT_WAKE_WORD = "Jarvis"


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
            while True:
                trigger_word = transcribe_audio()
                if trigger_word and wake_word.lower() in trigger_word.lower():
                    break

            # Una vez que se detecta la palabra clave, escuchar el comando después de la palabra clave
            say(generate_sentence(owner, SentenceType.GREETING))  # Selecciona una frase de saludo aleatoria
            command = transcribe_audio()
            print(f"[{owner.name.upper()[0]}] " + command)

            # Analizar el comando para determinar la acción a tomar.
            if any(word in command for word in
                   ["inicia", "activa"]) and "protocolo" in command and "buenos días" in command:
                say(f"¡Claro {owner.title}! Iniciando el protocolo buenos días...")
                await control_plug("on")
            elif any(word in command for word in
                     ["inicia", "activa"]) and "protocolo" in command and "buenas noches" in command:
                say(f"¡Por supuesto {owner.title}! Protocolo buenas noches iniciado...")
                await control_plug("off")
            elif "hora" in command and "es" in command:
                # Obtener la hora actual
                current_time = datetime.datetime.now().time()
                # Convertir la hora a un formato legible
                current_time_str = current_time.strftime("%I:%M %p")
                # Decir la hora actual utilizando el nombre del propietario
                say("Son las " + current_time_str + ", " + owner.title)
            elif any(word in command for word in
                     ["cuándo", "próximo", "siguiente"]) and "gran premio" in command and "fórmula 1" in command:
                message = next_gp.get_next_gp_message()
                say(message)
            elif "es" in command and any(word in command for word in ["nombre", "llamo"]):
                say(f"Su nombre es {owner.name}")
            elif any(word in command for word in ["actualiza", "modifica"]) and any(
                    word in command for word in ["datos", "propietario"]):
                owner = update_owner_info_interactive(owner)
            elif any(word in command for word in ["apágate", "apagar", "detente"]):
                # Selecciona una frase de despedida aleatoria
                farewell_response = generate_sentence(owner, SentenceType.FAREWELL)
                say(farewell_response)
                break
            elif any(word in command for word in ["quién", "cómo", "cuál"]) and any(
                    word in command for word in ["propietario", "soy"]):
                owner_info = get_owner_info(owner)
                say(owner_info)
            elif any(word in command for word in ["dime", "decir", "cuéntame"]) and any(
                    word in command for word in ["muerte", "vise", "matavise"]):
                say(get_random_death())
            # Agregar el comando para reiniciar el equipo
            elif any(word in command for word in ["reinicia", "reinciar"]) and any(
                    word in command for word in ["ordenador", "equipo", "sistema"]):
                await restart_computer()
            # Agregar el comando para cambiar la palabra clave
            elif "cambiar palabra clave" in command:
                config = update_config_interactive(config)
                if config:
                    wake_word = config.wake_word
            else:
                # Llama a la función para generar una respuesta
                response = generate_response(command, owner)
                say(response)
    except Exception as ex:
        say(f"Lamentablemente he sufrido el siguiente error: {ex}")


if __name__ == "__main__":
    asyncio.run(main())
