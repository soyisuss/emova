import random

def predict_emotion(face):

    emotions = ["Contento","Neutral","Descontento"]

    emotion = random.choice(emotions)

    confidence = round(random.uniform(0.6,0.9),2)

    return emotion, confidence