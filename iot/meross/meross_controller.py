import argparse
import asyncio
import os

from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager

import auth.auth as tkn

# Define the credentials
EMAIL = tkn.MEROSS_EMAIL
PASSWORD = tkn.MEROSS_PASSWORD


async def main(action, timer_minutes, timer_seconds):
    # Setup the HTTP client API from user-password
    http_api_client = await MerossHttpClient.async_from_user_password(email=EMAIL, password=PASSWORD,
                                                                      api_base_url="https://iot.meross.com")

    # Setup and start the device manager
    manager = MerossManager(http_client=http_api_client)
    await manager.async_init()

    # Retrieve all the MSS310 devices that are registered on this account
    await manager.async_device_discovery()
    plugs = manager.find_devices(device_type="mss310")

    if len(plugs) < 1:
        print("No MSS310 plugs found...")
    else:
        # Turn it on channel 0
        # Note that channel argument is optional for MSS310 as they only have one channel
        dev = plugs[0]

        # The first time we play with a device, we must update its status
        await dev.async_update()

        # We can now start playing with that
        if action == "on":
            print(f"Turning on {dev.name}...")
            await dev.async_turn_on(channel=0)
        elif action == "off":
            print(f"Turning off {dev.name}")
            await dev.async_turn_off(channel=0)

        if timer_minutes or timer_seconds:
            print(f"Waiting for {timer_minutes} minutes and {timer_seconds} seconds before turning it off")
            await asyncio.sleep(timer_minutes * 60 + timer_seconds)
            print(f"Turning off {dev.name}")
            await dev.async_turn_off(channel=0)

    # Close the manager and logout from http_api
    manager.close()
    await http_api_client.async_logout()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Control MSS310 plugs with optional timer.')
    parser.add_argument('action', choices=['on', 'off'], help='Action to perform: on or off')
    parser.add_argument('--timer_minutes', type=int, default=0, help='Timer minutes (default: 0)')
    parser.add_argument('--timer_seconds', type=int, default=0, help='Timer seconds (default: 0)')
    args = parser.parse_args()

    # Windows and python 3.8 requires to set up a specific event_loop_policy.
    # On Linux and MacOSX this is not necessary.
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args.action, args.timer_minutes, args.timer_seconds))
    loop.close()
