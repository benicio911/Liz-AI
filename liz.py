import speech_recognition as sr
import pyttsx3

# Initialize the speech recognizer and text-to-speech engine
r = sr.Recognizer()
engine = pyttsx3.init()

# Start listening for user input
with sr.Microphone() as source:
    print("Speak now!")
    audio = r.listen(source)

# Recognize the user's speech input
text = r.recognize_google(audio)

# Use the pre-trained model to generate an answer
answer = generate_answer(text)

# Convert the answer to speech
engine.say(answer)
engine.runAndWait()