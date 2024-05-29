import json

from storage.dtos.owner import Owner
from voice.voice_manager import say, transcribe_audio


def load_owner_from_json(filename):
    """
    Carga los datos del propietario desde un archivo JSON.

    Args:
        filename (str): La ruta del archivo JSON.

    Returns:
        Owner or None: El objeto Owner si se pudo cargar correctamente, None si ocurre un error.
    """
    try:
        with open(filename, "r", encoding="utf-8") as json_file:
            owner_data = json.load(json_file)
            return Owner(owner_data["name"], owner_data["age"], owner_data["title"])
    except FileNotFoundError:
        print("El archivo JSON del propietario no existe.")
        return None


def save_owner_to_json(filename, owner):
    """
    Guarda los datos del propietario en un archivo JSON.

    Args:
        filename (str): La ruta del archivo JSON.
        owner (Owner): El objeto Owner cuyos datos se van a guardar.
    """
    try:
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(owner.__dict__, json_file, ensure_ascii=False)
            print("Información del propietario guardada con éxito.")
    except FileNotFoundError:
        print("El archivo JSON del propietario no existe.")


def update_owner_info_interactive(owner):
    """
    Actualiza los datos del propietario de manera interactiva.

    Args:
        owner (Owner): El objeto Owner cuyos datos se van a actualizar.

    Returns:
        Owner: El objeto Owner actualizado.
    """
    try:
        say("¿Cuál es su nombre?")
        name = transcribe_audio()
        owner.name = name
        print(f"[{owner.name.upper()[0]}] " + name)

        say("¿Cuántos años tiene?")
        age = int(transcribe_audio())
        owner.age = age
        print(f"[{owner.name.upper()[0]}] " + str(age))

        say("¿Qué título le gustaría que usase? Por ejemplo: señor, señora, maestro, maestra...")
        title = transcribe_audio()
        owner.title = title
        print(f"[{owner.name.upper()[0]}] " + title)

        save_owner_to_json("storage/json/owner.json", owner)
        say("Información del propietario actualizada con éxito.")
        return owner
    except ValueError:
        say("No pude entender la información del propietario.")


def get_owner_info(owner):
    """
    Obtiene una frase que contiene toda la información disponible sobre el propietario.

    Args:
        owner (Owner): El objeto Owner del cual se obtendrá la información.

    Returns:
        str: Una frase que contiene toda la información disponible sobre el propietario.
    """
    owner_info = f"Soy el asistente JARVIS y aquí está la información sobre el propietario:\n" \
                 f"Nombre: {owner.name}\n" \
                 f"Edad: {owner.age}\n" \
                 f"Título: {owner.title}"
    return owner_info
