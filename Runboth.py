import subprocess

p1 = subprocess.Popen(["python3", "Main.py"])
p2 = subprocess.Popen(["python3", "frontend/app.py"])

# Wait for both processes to finish
p1.wait()
p2.wait()
