import random

import requests

# URL del archivo de texto
url = "https://raw.githubusercontent.com/kriseren/DatosMataVise/main/deaths.txt"


def get_random_death():
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
            number = description.split(".")[0].strip()
            description = description.split(".")[1].strip()
            return f"Muerte número {number}\n{description}\n{cause}"
        else:
            print(f"Formato inesperado en la línea: {random_line}. Seleccionando otra muerte...")


if __name__ == "__main__":
    random_death = get_random_death(url)
    print(random_death)
