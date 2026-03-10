import csv
import os

def save_emotion(task, emotion):

    os.makedirs("outputs", exist_ok=True)

    with open("outputs/emotions.csv","a",newline="") as f:

        writer = csv.writer(f)

        writer.writerow([task,emotion])