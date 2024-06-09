import json

from voice.voice_manager import say, get_command_input
from . import owner_manager
from ..dtos.config import Config


def load_config_from_json(filename):
    """
    Carga los datos de configuración desde un archivo JSON.

    Args:
        filename (str): La ruta del archivo JSON.

    Returns:
        Config or None: El objeto Config si se pudo cargar correctamente, None si ocurre un error.
    """
    try:
        with open(filename, "r", encoding="utf-8") as json_file:
            config_data = json.load(json_file)
            return Config(config_data.get("wake_word"), config_data.get("use_ai"))
    except FileNotFoundError:
        # Crear un objeto Config por defecto
        default_config = Config("jarvis")
        # Guardar el objeto Config por defecto en el archivo JSON
        save_config_to_json(filename, default_config)
        # Devolver el objeto Config por defecto
        return default_config


def save_config_to_json(filename, config):
    """
    Guarda los datos de configuración en un archivo JSON.

    Args:
        filename (str): La ruta del archivo JSON.
        config (Config): El objeto Config cuyos datos se van a guardar.
    """
    try:
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump({"wake_word": config.wake_word}, json_file, ensure_ascii=False)
            print("Información de configuración guardada con éxito.")
    except FileNotFoundError:
        print("El archivo JSON de configuración no existe.")


def update_config_interactive(config, input_mode):
    """
    Actualiza los datos de configuración de manera interactiva.

    Args:
        input_mode: El modo de entrada de comandos (text o voice).
        config (Config): El objeto Config cuyos datos se van a actualizar.

    Returns:
        Config: El objeto Config actualizado.
    """
    try:
        owner = owner_manager.load_owner_from_json("storage/json/owner.json")
        say("¿Cuál es la palabra clave para activarme?")
        wake_word = get_command_input(input_mode)
        config.wake_word = wake_word
        print(f"[{owner.name.upper()[0]}] " + wake_word)

        save_config_to_json("storage/json/config.json", config)
        say("Información de configuración actualizada con éxito.")
        return config
    except Exception as ex:
        say(f"No pude entender la información de configuración: {ex}")
        return None


def get_config_info(config):
    """
    Obtiene una frase que contiene toda la información disponible sobre la configuración.

    Args:
        config (Config): El objeto Config del cual se obtendrá la información.

    Returns:
        str: Una frase que contiene toda la información disponible sobre la configuración.
    """
    config_info = f"Aquí está la información sobre la configuración:\n" \
                  f"Wake Word: {config.wake_word}"
    return config_info
