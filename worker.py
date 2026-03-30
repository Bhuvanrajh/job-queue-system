import socket
import ssl
import time
import uuid

HOST = '10.170.8.47'   # 🔥 your server IP
PORT = 5000

# ✅ SECURE SSL (verification enabled)
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.load_verify_locations("server.crt")

# ✅ Unique Worker ID
worker_id = str(uuid.uuid4())[:6]


def execute_task(task):
    try:
        return str(eval(task))
    except:
        return "ERROR"


def start_worker():
    try:
        sock = socket.create_connection((HOST, PORT))
        s = context.wrap_socket(sock, server_hostname=HOST)

        s.send(b"WORKER\n")

        print(f"⚙️ Worker {worker_id} started...")
        print("⏳ Waiting for jobs...")

        buffer = ""

        while True:
            data = s.recv(1024).decode()

            if not data:
                print("❌ Server disconnected")
                break

            buffer += data

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()

                if line.startswith("JOB"):
                    try:
                        _, job_id, task = line.split(":", 2)

                        print(f"🚀 Worker {worker_id} processing {job_id} → {task}")

                        result = execute_task(task)

                        print(f"✅ Worker {worker_id} completed {job_id} → {result}")

                        s.send(f"DONE:{job_id}:{result}\n".encode())

                    except Exception as e:
                        print(f"❌ Worker {worker_id} parse error:", e)

                elif line == "NO_JOB":
                    time.sleep(1)
                    continue

    except Exception as e:
        print(f"❌ Worker {worker_id} failed to connect:", e)


if __name__ == "__main__":
    start_worker()