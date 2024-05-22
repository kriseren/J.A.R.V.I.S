import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    print("ID:", voice.id, "Name:", voice.name, "Gender:", voice.gender)
