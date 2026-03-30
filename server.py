import socket
import threading
import ssl
from queue import Queue
import time

HOST = '0.0.0.0'   # ✅ FIXED
PORT = 5000

job_queue = Queue()
job_results = {}
processing_jobs = {}

lock = threading.Lock()

worker_count = 0


def handle_client(conn, first_data, addr):
    buffer = first_data.strip() + "\n"

    while True:
        try:
            if "\n" not in buffer:
                data = conn.recv(1024).decode()
                if not data:
                    break
                buffer += data

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()

                if line.startswith("SUBMIT"):
                    _, job_id, task = line.split(":", 2)

                    with lock:
                        job_queue.put((job_id, task))

                    print(f"\nJob Received: {task}")
                    conn.send(f"ACK:{job_id}\n".encode())

                elif line.startswith("GET_RESULT"):
                    _, job_id = line.split(":")
                    result = job_results.get(job_id, "NOT_READY")
                    conn.send(f"RESULT:{job_id}:{result}\n".encode())

        except:
            break

    conn.close()


def handle_worker(conn, addr, worker_id):
    current_job = None
    buffer = ""

    try:
        while True:
            if not job_queue.empty():
                job_id, task = job_queue.get()

                with lock:
                    processing_jobs[job_id] = task
                    current_job = (job_id, task)

                print(f"Assigned to {worker_id}")
                conn.send(f"JOB:{job_id}:{task}\n".encode())

            else:
                conn.send(b"NO_JOB\n")
                time.sleep(1)
                continue

            while True:
                data = conn.recv(1024).decode()
                if not data:
                    raise Exception("Worker disconnected")

                buffer += data

                if "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()

                    if line.startswith("DONE"):
                        _, job_id, result = line.split(":", 2)

                        with lock:
                            job_results[job_id] = result
                            processing_jobs.pop(job_id, None)

                        print(f"{worker_id} Result: {result}")
                        break

    except:
        print("Worker stopped → Job reassigned")

        if current_job:
            job_queue.put(current_job)

    conn.close()


def identify_connection(conn, addr):
    global worker_count

    try:
        data = conn.recv(1024).decode().strip()

        if data == "WORKER":
            worker_count += 1
            worker_id = f"W{worker_count}"

            print(f"Worker connected | Total Workers: {worker_count}")

            handle_worker(conn, addr, worker_id)

            worker_count -= 1
            print(f"Worker disconnected | Total Workers: {worker_count}")

        else:
            print("Client request received")
            handle_client(conn, data, addr)

    except:
        conn.close()


def start_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")

    # ❌ REMOVED deprecated TLS warning line

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)

    print("SERVER RUNNING...\n")

    while True:
        client_sock, addr = server.accept()

        try:
            conn = context.wrap_socket(client_sock, server_side=True)
            threading.Thread(target=identify_connection, args=(conn, addr)).start()
        except:
            client_sock.close()


if __name__ == "__main__":
    start_server()