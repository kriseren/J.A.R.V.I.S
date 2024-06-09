import argparse
import asyncio
import os

from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager

import auth.auth as tkn

# Definir las credenciales
EMAIL = tkn.MEROSS_EMAIL
PASSWORD = tkn.MEROSS_PASSWORD


async def main(action, timer_minutes=0, timer_seconds=0):
    """
    Controla los enchufes MSS310 mediante acciones de encendido y apagado, con un temporizador opcional.

    Args:
        action (str): Acción a realizar ('on' o 'off').
        timer_minutes (int): Minutos del temporizador (opcional).
        timer_seconds (int): Segundos del temporizador (opcional).
    """
    # Configurar el cliente HTTP API con usuario y contraseña
    http_api_client = await MerossHttpClient.async_from_user_password(email=EMAIL, password=PASSWORD,
                                                                      api_base_url='https://iot.meross.com')

    # Configurar y arrancar el gestor de dispositivos
    manager = MerossManager(http_client=http_api_client)
    await manager.async_init()

    # Descubrir todos los dispositivos MSS310 registrados en esta cuenta
    await manager.async_device_discovery()
    plugs = manager.find_devices(device_type="mss310")

    if not plugs:
        print("No se encontraron enchufes MSS310...")
    else:
        # Seleccionar el primer dispositivo MSS310 encontrado
        dev = plugs[0]

        # Actualizar el estado del dispositivo
        await dev.async_update()

        # Ejecutar la acción especificada
        if action == "on":
            print(f"Encendiendo {dev.name}...")
            await dev.async_turn_on(channel=0)
        elif action == "off":
            print(f"Apagando {dev.name}...")
            await dev.async_turn_off(channel=0)

        # Si se especificó un temporizador, esperar y luego apagar el dispositivo
        if timer_minutes or timer_seconds:
            print(f"Esperando {timer_minutes} minutos y {timer_seconds} segundos antes de apagarlo")
            await asyncio.sleep(timer_minutes * 60 + timer_seconds)
            print(f"Apagando {dev.name}...")
            await dev.async_turn_off(channel=0)

    # Cerrar el gestor y cerrar sesión en el cliente HTTP
    manager.close()
    await http_api_client.async_logout()


if __name__ == '__main__':
    # Analizar los argumentos de la línea de comandos
    parser = argparse.ArgumentParser(description='Controlar enchufes MSS310 con temporizador opcional.')
    parser.add_argument('action', choices=['on', 'off'], help='Acción a realizar: encender o apagar')
    parser.add_argument('--timer_minutes', type=int, default=0, help='Minutos del temporizador (por defecto: 0)')
    parser.add_argument('--timer_seconds', type=int, default=0, help='Segundos del temporizador (por defecto: 0)')
    args = parser.parse_args()

    # En Windows y Python 3.8 es necesario configurar una política de bucle de eventos específica.
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Ejecutar la función principal asincrónica
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args.action, args.timer_minutes, args.timer_seconds))
    loop.close()
