import socket
import ssl
import uuid
import time
import tkinter as tk
from threading import Thread

HOST = '10.170.8.47'
PORT = 5000

# ✅ SECURE SSL
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.load_verify_locations("server.crt")

jobs = []
start_times = {}
job_tasks = {}
running = True


# 🔥 CLEAN OUTPUT FUNCTION
def add_output(task, job_id, result, time_taken):
    output.insert(tk.END, f"✔ Task: {task}\n", "submit")
    output.insert(tk.END, f"ID: {job_id}\n", "id")
    output.insert(tk.END, f"Result: {result}\n", "done")
    output.insert(tk.END, f"Time: {time_taken} sec\n\n", "time")
    output.see(tk.END)


def submit_job_gui():
    task = entry.get()

    if not task:
        return

    job_id = str(uuid.uuid4())[:8]

    try:
        with socket.create_connection((HOST, PORT)) as sock:
            with context.wrap_socket(sock, server_hostname=HOST) as s:
                s.send(f"SUBMIT:{job_id}:{task}\n".encode())
                s.recv(1024)

        # Store task for later display
        job_tasks[job_id] = task

        output.insert(tk.END, f"✔ Submitted: {task}\n", "submit")
        output.insert(tk.END, f"ID: {job_id}\n\n", "id")

        jobs.append(job_id)
        start_times[job_id] = time.time()

    except Exception as e:
        output.insert(tk.END, f"❌ Error: {e}\n\n")

    entry.delete(0, tk.END)


def get_result(job_id):
    try:
        with socket.create_connection((HOST, PORT)) as sock:
            with context.wrap_socket(sock, server_hostname=HOST) as s:
                s.send(f"GET_RESULT:{job_id}\n".encode())
                return s.recv(1024).decode().strip()
    except:
        return "ERROR"


def check_results():
    while running:
        for job_id in jobs[:]:
            result = get_result(job_id)

            if "NOT_READY" not in result and "ERROR" not in result:
                end_time = time.time()
                response_time = round(end_time - start_times[job_id], 2)

                task = job_tasks.get(job_id, "Unknown")

                # 🔥 CLEAN DISPLAY
                add_output(task, job_id, result.split(":")[-1], response_time)

                jobs.remove(job_id)

        time.sleep(2)


# 🔷 GUI SETUP
root = tk.Tk()
root.title("Distributed Job Queue")
root.geometry("600x500")
root.configure(bg="#121212")

# Title
title = tk.Label(root, text="Distributed Job Queue",
                 font=("Segoe UI", 18, "bold"),
                 bg="#121212", fg="#00ffc8")
title.pack(pady=10)

# Input Frame
input_frame = tk.Frame(root, bg="#121212")
input_frame.pack(pady=10)

entry = tk.Entry(input_frame, width=35, font=("Segoe UI", 12))
entry.grid(row=0, column=0, padx=5)

submit_btn = tk.Button(input_frame,
                       text="Submit",
                       font=("Segoe UI", 10, "bold"),
                       bg="#00ffc8",
                       fg="black",
                       width=10,
                       command=submit_job_gui)
submit_btn.grid(row=0, column=1, padx=5)

# Result Label
result_label = tk.Label(root,
                        text="Results",
                        font=("Segoe UI", 12, "bold"),
                        bg="#121212",
                        fg="white")
result_label.pack(anchor="w", padx=20)

# Scrollable Output
frame = tk.Frame(root)
frame.pack(padx=20, pady=5, fill="both", expand=True)

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side="right", fill="y")

output = tk.Text(frame,
                 height=15,
                 bg="#1e1e1e",
                 fg="white",
                 font=("Consolas", 10),
                 yscrollcommand=scrollbar.set)

output.pack(fill="both", expand=True)
scrollbar.config(command=output.yview)

# Colors
output.tag_config("submit", foreground="#00ffc8")
output.tag_config("id", foreground="#aaaaaa")
output.tag_config("done", foreground="#00ff00")
output.tag_config("time", foreground="#ffaa00")

# Start thread
Thread(target=check_results, daemon=True).start()

root.mainloop()
running = False