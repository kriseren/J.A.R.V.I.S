import random

import requests

# URL del archivo de texto
URL = "https://raw.githubusercontent.com/kriseren/DatosMataVise/main/deaths.txt"


def get_random_death(url=URL):
    """
    Descarga una lista de muertes de un archivo de texto en línea y devuelve una muerte aleatoria.

    Args:
        url (str): URL del archivo de texto con las muertes.

    Returns:
        str: Una cadena formateada con el número de la muerte, su descripción y la causa de la muerte.
    """
    # Descargar el archivo de texto
    response = requests.get(url)
    response.raise_for_status()  # Asegurarse de que la solicitud se realizó correctamente

    # Leer todas las líneas del archivo
    lines = response.text.splitlines()

    while True:
        # Seleccionar una línea al azar
        random_line = random.choice(lines)

        # Dividir la línea en número, descripción y causa de la muerte
        parts = random_line.split(" ~ ")
        if len(parts) == 2:
            description, cause = parts
            number, desc_text = description.split(".", 1)
            return f"Muerte número {number.strip()}\n{desc_text.strip()}\n{cause.strip()}"
        else:
            print(f"Formato inesperado en la línea: {random_line}. Seleccionando otra muerte...")


if __name__ == "__main__":
    random_death = get_random_death()
    print(random_death)
