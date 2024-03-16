import google.generativeai as genai
import time
from pylatexenc.latex2text import LatexNodes2Text

genai.configure(api_key="AIzaSyDdDpX2sFbSHzkxeyUCOER4Fjccuh-9JwI")
import tkinter as tk
import random
from tkinter import messagebox, font

def latex_to_unicode(latex_str):
    return LatexNodes2Text().latex_to_text(latex_str)
# Define the PQRST functions
def preview_material(material):
    prompt= f"**Spark Curiosity!** Imagine you're explaining this to a friend who's new to it. What's the most interesting thing you'd tell them about {material}?"
    response=genai.chat(model="models/chat-bison-001",messages=prompt,temperature=0.5)
    return latex_to_unicode(response.last)

def ask_questions(material):
    prompt_options = [
        f"\n**Headline Challenge!** If {material} were a news headline, what would it be?",
        f"\n**Prediction Game!** Based on the title or preview of {material}, what do you think you'll learn about?",
        f"\n**Curiosity Prompt!** What specific questions do you have about this topic {material} right now?"
    ]
    prompt = random.choice(prompt_options)
    response = genai.chat(model="models/chat-bison-001", messages=prompt, temperature=0.5)
    return latex_to_unicode(response.last)

def read_and_study(material):
    prompt=f"**Teach me in detail about {material}(Please Explain with ascii diagrams if possible)."
    response=genai.chat(model="models/chat-bison-001",messages=prompt,temperature=0.5)
    return latex_to_unicode(response.last)

def summarize_key_points(material):
    prompt = f"**Reinforce Learning!** \nIf you could explain this topic in just 3-5 sentences to someone else, what would you say?\n"
    summary = input(prompt)
    print()
    # Here you can add logic to analyze the summary and provide feedback
    if summary:
        feedback = f"This is my summary: {summary} ;please give me a score out of 10 and higlights the points i missed out and what should i improve regarding the topic {material}?."
        response=genai.chat(model="models/chat-bison-001",messages=feedback,temperature=0.5)
        return latex_to_unicode(response.last)
    else:
        return "summary not given in the python window"

def test_understanding(material):
    prompt_options = [
        f"\n**Self-Quiz!** Create your own multiple-choice, true/false, or fill-in-the-blank questions based on {material}.",
        f"\n**Challenge a Friend!** Explain a concept to a friend and see if they can understand the {material}.",
        f"\n**Gamification!** Create a quiz python app or learning game (e.g., Kahoot!, Quizlet Live) to test yourself in a fun way about the topic {material}."
    ]
    prompt = random.choice(prompt_options)
    response=genai.chat(model="models/chat-bison-001",messages=prompt,temperature=0.5)
    return latex_to_unicode(response.last)

# Define the study session function
def pqrs_t_study_session():
    material = entry.get()
    output.delete(1.0, tk.END)
    output.insert(tk.END, preview_material(material))
    root.after(25000, lambda: output.insert(tk.END, ask_questions(material)))
    root.after(50000, lambda: output.insert(tk.END, read_and_study(material)))
    root.after(750000, lambda: output.insert(tk.END, summarize_key_points(material)))
    root.after(1200000, lambda: output.insert(tk.END, test_understanding(material)))

# Define the countdown function
def countdown(time_left):
    if time_left > -1:
        mins, secs = divmod(time_left, 60)
        timer.set("{:02d}:{:02d}".format(mins, secs))
        root.after(1000, countdown, time_left - 1)
    else:
        messagebox.showinfo("Time's up!", "It's time to take a break!")

# Create the tkinter window
root = tk.Tk()
root.title("PQRST Study Session")
root.configure(bg='light blue')

# Create the text output widget
output = tk.Text(root, width=75, height=20, bg='white', fg='black', font=("Helvetica",12))
output.pack(pady=10)

# Create the entry widget for the study topic
entry = tk.Entry(root, width=50)
entry.pack(pady=10)

# Create the timer label
timer = tk.StringVar()
timer.set("25:00")
timer_label = tk.Label(root, textvariable=timer, font=('Helvetica', 20), bg='light blue')
timer_label.pack()

# Create the study button
study_button = tk.Button(root, text="Start Study Session", command=lambda: [pqrs_t_study_session(), countdown(25*60)], bg='green', fg='white')
study_button.pack()

# Run the tkinter main loop
root.mainloop()
