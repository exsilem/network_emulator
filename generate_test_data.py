import csv
import random
import os

os.makedirs("data/distributions", exist_ok=True)

# delays.csv: равномерное распределение 50-150 мс
with open("data/distributions/delays.csv", "w", newline="") as f:
    w = csv.writer(f)
    for _ in range(500):
        w.writerow([random.uniform(50, 150)])

# jitter.csv: нормальное распределение (μ=10, σ=3)
with open("data/distributions/jitter.csv", "w", newline="") as f:
    w = csv.writer(f)
    for _ in range(500):
        w.writerow([max(0, random.gauss(10, 3))])

# bandwidth.csv: нормальное распределение (μ=1 Мбит/с, σ=100 кбит/с)
with open("data/distributions/bandwidth.csv", "w", newline="") as f:
    w = csv.writer(f)
    for _ in range(500):
        w.writerow([max(100_000, random.gauss(1_000_000, 100_000))])

print("Test data generated in data/distributions/")