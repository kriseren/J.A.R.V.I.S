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
        str: El mensaje.
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
            "Hoy es el día. ¿Conseguirá el nano su victoria número 33? "
            "Todos a ver la carrera a las {time}".format(time=format_spanish_timezone(time))
        )
    elif days_left <= 3:
        if "Sprint" in gp:
            message = (
                "Apenas quedan {days} días para volver a disfrutar. "
                "Entrenamientos libres uno: {practice1_day} a las {practice1_time}. "
                "Clasificación Sprint: {practice2_day} a las {practice2_time}. "
                "Carrera Sprint: {sprint_day} a las {sprint_time}. "
                "Clasificación: {qualifying_day} a las {qualifying_time}. "
                "Carrera: {race_day} a las {race_time}.".format(
                    days=days_left,
                    practice1_day=get_day_of_the_week(gp["FirstPractice"]["date"]),
                    practice1_time=format_spanish_timezone(gp["FirstPractice"]["time"]),
                    practice2_day=get_day_of_the_week(gp["SecondPractice"]["date"]),
                    practice2_time=format_spanish_timezone(gp["SecondPractice"]["time"]),
                    sprint_day=get_day_of_the_week(gp["Sprint"]["date"]),
                    sprint_time=format_spanish_timezone(gp["Sprint"]["time"]),
                    qualifying_day=get_day_of_the_week(gp["Qualifying"]["date"]),
                    qualifying_time=format_spanish_timezone(gp["Qualifying"]["time"]),
                    race_day=get_day_of_the_week(date),
                    race_time=format_spanish_timezone(time),
                )
            )
        else:
            message = (
                "Solo {days} días para disfrutarlo. "
                "Entrenamientos libres uno: {practice1_day} a las {practice1_time}. "
                "Entrenamientos libres dos: {practice2_day} a las {practice2_time}. "
                "Entrenamientos libres tres: {practice3_day} a las {practice3_time}. "
                "Clasificación: {qualifying_day} a las {qualifying_time}. "
                "Carrera: {race_day} a las {race_time}.".format(
                    days=days_left,
                    practice1_day=get_day_of_the_week(gp["FirstPractice"]["date"]),
                    practice1_time=format_spanish_timezone(gp["FirstPractice"]["time"]),
                    practice2_day=get_day_of_the_week(gp["SecondPractice"]["date"]),
                    practice2_time=format_spanish_timezone(gp["SecondPractice"]["time"]),
                    practice3_day=get_day_of_the_week(gp["ThirdPractice"]["date"]),
                    practice3_time=format_spanish_timezone(gp["ThirdPractice"]["time"]),
                    qualifying_day=get_day_of_the_week(gp["Qualifying"]["date"]),
                    qualifying_time=format_spanish_timezone(gp["Qualifying"]["time"]),
                    race_day=get_day_of_the_week(date),
                    race_time=format_spanish_timezone(time),
                )
            )
    elif days_left < 7:
        message = (
            "Entramos en semana de carrera y quedan {days} días para el Gran Premio de {country} en {circuit} "
            "este {date} a las {time}.".format(
                days=days_left,
                country=country,
                circuit=circuit,
                date=date,
                time=format_spanish_timezone(time),
            )
        )
    else:
        message = (
            "Quedan {days} días para el Gran Premio de {country} en {circuit}. Fecha: {date}. Hora: {time}.".format(
                days=days_left,
                country=country,
                circuit=circuit,
                date=date,
                time=format_spanish_timezone(time),
            )
        )

    return message


def format_spanish_timezone(time_str):
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
    return hora_fecha_madrid.strftime("%H:%M")


def get_day_of_the_week(date_str):
    """
    Devuelve el nombre del día de la semana para una fecha dada.

    Args:
        date_str (str): La fecha en formato YYYY-MM-DD.

    Returns:
        str: El nombre del día de la semana (por ejemplo: "Domingo").
    """
    try:
        locale.setlocale(locale.LC_TIME, "es_ES.utf8")
    except locale.Error:
        pass
    fecha = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return fecha.strftime("%A").capitalize()
