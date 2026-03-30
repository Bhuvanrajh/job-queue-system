Distributed Job Queue System

Overview:
This project implements a Distributed Job Queue System using low-level TCP socket programming with SSL/TLS-secured communication.
It enables multiple clients to submit jobs while multiple worker nodes process them concurrently in a reliable, fault-tolerant, and secure distributed environment.

Features:
- TCP socket-based communication
- SSL/TLS encrypted and verified communication
- Multi-client support
- Multi-worker support
- Centralized job queue (FIFO scheduling)
- Concurrent processing using multithreading
- Fault tolerance (automatic job re-queue on worker failure)
- Worker and client connection tracking
- Job assignment monitoring (which worker processes which job)

System Architecture:
Client → Server → Worker

Client: Submits tasks and retrieves results  
Server: Manages queue, assigns jobs, tracks nodes  
Worker: Processes tasks and returns results  

Workflow:
1. Client sends a job to the server
2. Server stores the job in a queue
3. Worker connects and requests a job
4. Server assigns job dynamically
5. Worker processes the job
6. Worker sends result back
7. Client retrieves result

Requirements:
- Python 3.x
- Required library:
  pip install pyopenssl

How to Run:
1. Generate SSL Certificate
   python generate_cert.py

2. Start Server
   python server.py

3. Start Worker (run multiple instances)
   python worker.py

4. Start Client
   python client.py

Performance:
- Supports concurrent clients and workers
- Response time increases with load
- Throughput improves with additional workers
- Efficient load distribution using queue system

Security:
- Uses SSL/TLS with certificate verification
- Prevents data interception (encryption)
- Ensures server authenticity (authentication)
- Protects against man-in-the-middle attacks

Monitoring and Logging:
- Tracks active workers and clients
- Logs connection and disconnection events
- Displays job origin and assignment
- Shows fault handling and re-queue events

Project Structure:
project/
│
├── server.py
├── worker.py
├── client.py
├── generate_cert.py
└── server.crt

Conclusion:
This project demonstrates:
- Distributed system design
- Secure communication using SSL/TLS
- Concurrent processing with multithreading
- Fault-tolerant job execution