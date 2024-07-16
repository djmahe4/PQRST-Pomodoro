import tkinter as tk
import os
from tkinter import simpledialog, messagebox
import time
import threading
import random
import google.generativeai as genai
from time import sleep
import datetime
import re
import random
from dotenv import load_dotenv, find_dotenv
from pylatexenc.latex2text import LatexNodes2Text

#colours=['red','purple','blue','green']
def latex_to_unicode(latex_str):
    return LatexNodes2Text().latex_to_text(latex_str)
# Find or create .env file
env_path = find_dotenv()
if env_path == "":
    with open('.env', 'w') as f:
        pass
env_path = find_dotenv()

# Load existing .env file or create one if it doesn't exist
load_dotenv(find_dotenv(), override=True)

# Check if API key is in environment variables
api_key = os.getenv('GENERATIVE_AI_KEY')
if api_key is None:
    # If API key is not set, ask the user for it
    api_key = input('Please enter your API key from https://ai.google.dev: ')
    # Store the API key in the .env file
    with open(find_dotenv(), 'a') as f:
        f.write(f'GENERATIVE_AI_KEY={api_key}\n')
    print("API key stored successfully!")

load_dotenv()
genai.configure(api_key=os.environ["GENERATIVE_AI_KEY"])

generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 0,
    "response_mime_type": "text/plain"
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
]

model = genai.GenerativeModel(
    model_name="gemini-1.0-pro",
    safety_settings=safety_settings,
    generation_config=generation_config
)

chat_session = model.start_chat(history=[])

def append_pqrst_markdown(subject, section, content):
  """
  Appends a markdown section to a file for studying using the PQrst method.

  Args:
      subject (str): The subject of the study material.
      section (str): The PQrst section (e.g., "P", "Q", "R", "S", "T").
      content (str): The content for the specified section.
  """
  # Create timestamp for clarity
  timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  filename = f"{subject}.md"

  # Construct markdown text with section heading
  markdown_text = f"""

## {subject} - {timestamp}

**{section}:**

{content}

"""

  # Open the file in append mode (a+) to create it if it doesn't exist
  with open(filename, "a+",encoding='utf-8') as file:
    file.write(markdown_text)

def gemini_ai_query(query):
    # This function will communicate with Gemini AI to get the output
    # Replace with actual Gemini AI API calls
    response = chat_session.send_message(query)
    response=latex_to_unicode(response.text)
    return response#.text

def generate_questions(query,chat_session):
    # This function will communicate with Gemini AI to get the output
    # Replace with actual Gemini AI API calls
    global question_answer
    try:
        while True:
            response = chat_session.send_message(query)
            # Extract the question and answer from the generated text
            question_answer = response.text.replace("*","").replace("**","")

            # Define a pattern to extract the question, options, and answer
            #pattern = r"\d+\.(.*?)\n\((a)\)(.*?)\n\((b)\)(.*?)\n\((c)\)(.*?)\n\((d)\)(.*?)\n\n\*\*AnswerKey:\*\*\n(\d+)\.\((.)\)"

            # Find all matches in the input text
            #matches = re.findall(pattern, question_answer, re.DOTALL)
            matches=question_answer.split("\n")

            # Create a list of dictionaries, each containing question, options, and answer
            questions_list = []

            diction={
                'question':"",
                'options':['','','','']
            }
            questions_list.append(diction)
            for match in matches:
                if match==" " or match=="" :#or "answer" in match.lower():
                    continue
                if 'answer' in match.lower():
                    match2 = re.search(r"\((.)\)", match)
                    if match2:
                        extracted_character = match2.group(1)
                        diction.update({"answer": extracted_character})
                #if type(match[0])==int:
                try:
                    if int(match[0]) and len(match)>10:
                        diction["question"]=match[3:]
                        print(match[3:])
                except ValueError:
                    pass
                if diction["question"]=="" and match.endswith("?"):
                    diction["question"]=match
                if match[1]=='a':
                    diction['options'][0]=match
                if match[1]=='b':
                    diction['options'][1]=match
                if match[1]=='c':
                    diction['options'][2]=match
                if match[1]=='d':
                    diction['options'][3] = match
                    diction = {
                        'question': "",
                        'options': ['','','','']
                    }
                    questions_list.append(diction)
                qmatch = re.match(r"(\d+)\.\s*\((\w)\)", match)
                if qmatch:
                    question_number, answer = qmatch.groups()
                    question_number=int(question_number)
                    print(f"Question {question_number}: Answer = {answer}")
                    # options=questions_list[question_number]["options"]
                    diction=questions_list[question_number-1]
                    diction.update({"answer": answer})
                    questions_list[question_number-1]=diction
                #else:
                    #diction["question"]+=match
            break
    except questions_list==[] or questions_list[0]['question']=='' or len(questions_list)>=3:
        sleep(10)
        print("retrying..")

    # Print the list of dictionaries
    print(questions_list)
    append_pqrst_markdown(query,"Test",question_answer)
    #else:
    #return response.text.replace("*","")
    return questions_list


class Timer:
    def __init__(self, duration, update_ui_callback, on_finish_callback):
        self.duration = duration
        self.time_left = duration
        self.update_ui_callback = update_ui_callback
        self.on_finish_callback = on_finish_callback
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._countdown).start()

    def skip(self):
        self.running = False
        self.on_finish_callback()

    def extend(self):
        self.time_left += 5 * 60

    def _countdown(self):
        while self.running and self.time_left > 0:
            time.sleep(1)
            self.time_left -= 1
            self.update_ui_callback(self.time_left)
        if self.running:
            self.running = False
            self.on_finish_callback()

class PQRSApp:
    def __init__(self, rt):
        self.root = rt
        self.root.title("PQRST Learning Method with Pomodoro")
        self.setup_ui()
        self.questions = []
        self.current_question_index = 0
        self.score = 0

    def setup_ui(self):
        # Define UI elements and layout
        self.topic_label = tk.Label(self.root, text="Enter your learning topic:")
        self.topic_label.pack()
        self.topic_entry = tk.Entry(self.root)
        self.topic_entry.pack()
        self.start_button = tk.Button(self.root, text="Start", command=self.start_pqrs)
        self.start_button.pack()
        self.output_text = tk.Text(self.root, height=20, width=80)
        self.output_text.pack()
        self.timer_label = tk.Label(self.root, text="Time left: ")
        self.timer_label.pack()
        self.skip_button = tk.Button(self.root, text="Skip", command=self.skip_timer)
        self.skip_button.pack()
        self.extend_button = tk.Button(self.root, text="Extend", command=self.extend_timer)
        self.extend_button.pack()

    def start_pqrs(self):
        #global topic
        topic = self.topic_entry.get()
        self.topic= topic
        if topic:
            self.output_text.insert(tk.END, f"Starting PQRST method for topic: {topic}\n")
            self.run_step("Preview", 5 * 60, f"Preview of {topic}", self.question)

    def run_step(self, step_name, duration, query, next_step_callback):
        self.output_text.insert(tk.END, f"{step_name}:\n") #fg=random.choice(colours))
        #try:
        ai_output = gemini_ai_query(query)
        #except genai.types.StopCandidateException:
            #sleep(5)
            #ai_output = gemini_ai_query(query)
        self.output_text.insert(tk.END, str(ai_output) + "\n\n"+ "-"*58+"\n\n")
        self.timer = Timer(duration, self.update_timer_label, next_step_callback)
        self.timer.start()
        append_pqrst_markdown(self.topic, step_name, ai_output)
        self.next_step_callback = next_step_callback

    def update_timer_label(self, time_left):
        minutes, seconds = divmod(time_left, 60)
        self.timer_label.config(text=f"Time left: {minutes:02}:{seconds:02}")

    def skip_timer(self):
        if self.timer:
            self.timer.skip()
            self.output_text.insert(tk.END, "Timer skipped.\n")

    def extend_timer(self):
        if self.timer:
            self.timer.extend()
            self.output_text.insert(tk.END, "Timer extended by 5 minutes.\n")

    def preview(self):
        self.run_step("Preview", 1 * 60, "Preview the topic", self.question)

    def question(self):
        self.run_step("Questions", 10 * 60, "Formulate questions and answers about the topic for clear understanding of concepts", self.read)

    def read(self):
        self.run_step("Read", 25 * 60, "Reading material about the topic", self.summarize)

    def summarize(self):
        self.run_step("Summarize", 10 * 60, "Summary of the topic", self.test)

    def test(self):
        topic = self.topic_entry.get()
        self.questions = generate_questions(f"Formulate mcq quiz on {topic} with answers",chat_session)
        #random.shuffle(self.questions)  # Shuffle the questions
        self.score = 0
        self.current_question_index = 0
        self.test_window = tk.Toplevel(self.root)
        self.test_window.title("Test Your Knowledge")
        self.question_label = tk.Label(self.test_window, text="")
        self.question_label.pack()
        self.option_buttons = []
        for i in range(4):
            button = tk.Button(self.test_window, text="", command=lambda idx=i: self.check_answer(idx))
            button.pack()
            self.option_buttons.append(button)
        self.score_label = tk.Label(self.test_window, text="Score: 0")
        self.score_label.pack()
        self.load_next_question()

    def load_next_question(self):
        if self.questions[self.current_question_index]["question"]=="":
            self.test_window.destroy()
            self.test()
        if self.current_question_index < len(self.questions) or self.questions[self.current_question_index]["answer"]!="" :
            question_data = self.questions[self.current_question_index]
            question = question_data["question"]
            options = question_data["options"]
            self.question_label.config(text=question)
            #random.shuffle(options)  # Shuffle the options
            for i in range(4):
                self.option_buttons[i].config(text=options[i])
        else:
            self.finish_test()

    def check_answer(self, selected_index):
        #correct_answer = self.questions[self.current_question_index]["options"][0]  # First option is correct
        user_answer = self.option_buttons[selected_index].cget("text")
        correct_answer = self.questions[self.current_question_index]["answer"]
        check = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
        ca = self.questions[self.current_question_index]["options"][check[correct_answer]]
        if user_answer == correct_answer:
            self.score += 1
        self.current_question_index += 1
        self.score_label.config(text=f"Score: {self.score}")
        self.load_next_question()

    def finish_test(self):
        messagebox.showinfo("Test Completed", f"Your final score is: {self.score}")
        self.test_window.destroy()
        self.finish()

    def finish(self):
        self.output_text.insert(tk.END, "PQRST method completed. Good job!\n")
        root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PQRSApp(root)
    root.mainloop()
