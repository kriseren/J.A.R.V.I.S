import pyttsx3
import speech_recognition as sr

# Inicializar el motor TTS (Texto a Voz)
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)  # El id controla la voz.


def get_command_input(input_mode):
    """Obtiene el comando según el modo de entrada."""
    if input_mode == "voice":
        return transcribe_audio()
    elif input_mode == "text":
        return input("Ingrese el comando: ")
    else:
        raise ValueError("Modo de entrada no soportado.")


def say(text, rate=210):
    """
    Función para que el programa "diga" un texto.

    Args:
        text (str): El texto que se quiere "decir".
        rate (int): La velocidad de reproducción del texto.
    """
    # Imprimir por pantalla el texto.
    print(f"[J] {text}")
    # Utilizar el motor TTS para decir el texto
    engine.setProperty("rate", rate)  # Ajustar la velocidad de reproducción
    engine.say(text)
    engine.runAndWait()


def transcribe_audio(timeout=2):
    """
    Función para transcribir audio del micrófono.

    Args:
        timeout (int): Tiempo máximo para esperar que se detecte audio.

    Returns:
        str: El texto transcrito
        o, o una cadena vacía si no se pudo transcribir.
    """
    # Crear un objeto reconocedor de voz
    recognizer = sr.Recognizer()

    # Ajustar el umbral de energía
    recognizer.energy_threshold = 900

    # Usar el micrófono como fuente de audio
    with sr.Microphone() as source:
        try:
            # Escuchar el audio del micrófono con un tiempo de espera máximo definido
            audio = recognizer.listen(source, timeout=timeout)
        except sr.WaitTimeoutError:
            return ""

    try:
        # Transcribir el audio utilizando el servicio de Google
        text = recognizer.recognize_google(audio, language="es-ES")
        return text.lower()
    except sr.UnknownValueError:
        print("No se pudo entender el audio")
    except sr.RequestError as e:
        print("Error al solicitar la transcripción; {0}".format(e))
