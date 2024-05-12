import datetime
import locale

import pytz
import requests


def get_next_gp(gps):
    """
    Obtiene el siguiente Gran Premio a partir de una lista de Grandes Premios.

    Args:
        gps (list): Lista de Grandes Premios.

    Returns:
        dict: Información del próximo Gran Premio.
    """
    today = datetime.date.today()
    next_gp = min(
        gps,
        key=lambda gp: (
            datetime.datetime.strptime(gp["date"], "%Y-%m-%d").date() - today
            if datetime.datetime.strptime(gp["date"], "%Y-%m-%d").date() >= today
            else datetime.timedelta(days=365 * 100)
        ),
    )
    return next_gp


def get_next_gp_message():
    """
    Crea el mensaje y el tweet para el Gran Premio dado.

    Returns:
        list: Una lista que contiene el mensaje y el tweet.
    """

    response = requests.get("https://ergast.com/api/f1/current.json")
    gps = response.json()["MRData"]["RaceTable"]["Races"]
    gp = get_next_gp(gps)

    country = gp["Circuit"]["Location"]["country"]
    circuit = gp["Circuit"]["circuitName"]
    date = gp["date"]
    time = gp["time"]
    days_left = (
            datetime.datetime.strptime(gp["date"], "%Y-%m-%d").date()
            - datetime.date.today()
    ).days

    if days_left == 0:
        message = (
            f"🏁 ¡HOY ES EL DÍA SEÑORAS Y SEÑORES! 🏁\n¿Conseguirá el nano su victoria Nº33? Todos a ver la carrera a "
            f"las {format_spanish_timezone(time)}"
        )

    elif days_left <= 3:
        if "Sprint" in gp:
            message = (
                f"¡Apenas quedan {days_left} días para volver a disfrutar! 👇🏼\n\n"
                f"🏃 Ent. libres 1: {get_day_of_the_week(gp['FirstPractice']['date'])} a las {format_spanish_timezone(gp['FirstPractice']['time'])}\n\n"
                f"⏱ Clasif. Sprint: {get_day_of_the_week(gp['SecondPractice']['date'])} a las {format_spanish_timezone(gp['SecondPractice']['time'])}\n\n"
                f"🏁 Carrera Sprint: {get_day_of_the_week(gp['Sprint']['date'])} a las {format_spanish_timezone(gp['Sprint']['time'])}\n\n"
                f"⏱ Clasificación: {get_day_of_the_week(gp['Qualifying']['date'])} a las {format_spanish_timezone(gp['Qualifying']['time'])}\n\n"
                f"🏁 Carrera: {get_day_of_the_week(date)} a las {format_spanish_timezone(time)}\n"
            )
        else:
            message = (
                f"¡Solo {days_left} días para disfrutarlo! 👇🏼\n\n"
                f"🏃 Ent. libres 1: {get_day_of_the_week(gp['FirstPractice']['date'])} a las {format_spanish_timezone(gp['FirstPractice']['time'])}\n\n"
                f"🏃 Ent. libres 2: {get_day_of_the_week(gp['SecondPractice']['date'])} a las {format_spanish_timezone(gp['SecondPractice']['time'])}\n\n"
                f"🏃 Ent. libres 3: {get_day_of_the_week(gp['ThirdPractice']['date'])} a las {format_spanish_timezone(gp['ThirdPractice']['time'])}\n\n"
                f"⏱ Clasificación: {get_day_of_the_week(gp['Qualifying']['date'])} a las {format_spanish_timezone(gp['Qualifying']['time'])}\n\n"
                f"🏁 Carrera: {get_day_of_the_week(date)} a las {format_spanish_timezone(time)}\n"
            )

    elif days_left < 7:
        message = f"Entramos en semana de carrera y quedan {days_left} días para el Gran Premio de {country} en {circuit} este {date} a las {format_spanish_timezone(time)}"

    else:
        message = f"Quedan {days_left} días para el Gran Premio de {country} en {circuit}. Fecha: {date}. Hora: {format_spanish_timezone(time)}"

    return message


def format_spanish_timezone(time_str: str):
    """
    Convierte una hora en formato UTC (Z) a la hora en la zona horaria de Madrid.

    Args:
        time_str (str): La hora en formato UTC (por ejemplo: "09:00:00Z").

    Returns:
        str: La hora convertida en la zona horaria de Madrid (por ejemplo: "11:00:00").
    """
    time_utc = datetime.datetime.strptime(time_str[:-1], "%H:%M:%S").time()
    timezone_madrid = pytz.timezone("Europe/Madrid")
    local_time_utc = datetime.datetime.utcnow().date()
    temp_datetime_utc = datetime.datetime.combine(local_time_utc, time_utc)
    hora_fecha_madrid = temp_datetime_utc.replace(tzinfo=pytz.utc).astimezone(
        timezone_madrid
    )
    formatted_time = hora_fecha_madrid.strftime("%H:%M")
    return formatted_time


def get_day_of_the_week(date: str):
    """
    Devuelve el nombre del día de la semana para una fecha dada.

    Args:
        date (str): La fecha en formato YYYY-MM-DD.

    Returns:
        str: El nombre del día de la semana (por ejemplo: "Domingo").
    """
    try:
        locale.setlocale(locale.LC_TIME, "es_ES.utf8")
    except locale.Error:
        pass
    fecha = datetime.datetime.strptime(date, "%Y-%m-%d")
    nombre_dia = fecha.strftime("%A").capitalize()
    return nombre_dia
