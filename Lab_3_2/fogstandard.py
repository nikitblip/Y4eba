"""
viz_phone_pipeline_bilingual.py

Билингвальная визуализация конвейера: Датчик → Fog → Курьер → Телефон.
Bilingual visualization of the pipeline: Sensor → Fog → Courier → Phone.

Показываем / We show:
  • Сквозная задержка "от датчика до телефона" для каждой задачи.
    End‑to‑end latency "sensor → phone" per task.
  • Размер буфера телефона по мере прибытия сообщений.
    Phone buffer size as messages arrive.
  • В консоли печатаются метрики на русском и английском.
    Console prints metrics in Russian and English.
"""
import random, statistics
import matplotlib.pyplot as plt

PIPELINE_RU = "Датчик → Fog → Курьер → Телефон"
PIPELINE_EN = "Sensor → Fog → Courier → Phone"

def simulate(n_tasks=30, seed=7):
    random.seed(seed)
    # Processing times (ms) per stage / Времена обработки (мс) на каждом этапе:
    sensor  = [random.randint(20, 60) for _ in range(n_tasks)]   # Sensor / Датчик
    fog     = [random.randint(30, 80) for _ in range(n_tasks)]   # Fog node / Fog‑узел
    courier = [random.randint(10, 40) for _ in range(n_tasks)]   # Courier / Курьер

    # End‑to‑end latency per task is the sum of stage times:
    # Сквозная задержка на задачу — это сумма времен этапов:
    latencies = [s + f + c for s, f, c in zip(sensor, fog, courier)]

    # Phone buffer: phone "reads" messages every read_interval_ms
    # Буфер телефона: телефон "читает" сообщения каждые read_interval_ms
    read_interval_ms = 120
    time = 0
    buffer_sizes = []
    buf = 0
    for L in latencies:
        time += L
        reads = time // read_interval_ms
        for _ in range(int(reads)):
            if buf > 0:
                buf -= 1
        buf += 1
        buffer_sizes.append(buf)

    avg_latency = statistics.mean(latencies)
    p95 = statistics.quantiles(latencies, n=20)[18]  # ≈95th percentile

    return latencies, buffer_sizes, avg_latency, p95

def plot(latencies, buffer_sizes):
    # Plot 1: end‑to‑end latency (RU/EN)
    plt.figure(figsize=(8, 4.5))
    x = range(1, len(latencies)+1)
    plt.plot(x, latencies, marker='o')
    plt.title(f"Сквозная задержка {PIPELINE_RU}\nEnd-to-End Latency {PIPELINE_EN}")
    plt.xlabel("Номер задачи / Task #")
    plt.ylabel("Задержка, мс / Latency, ms")
    # Пояснение прямо на графике:
    plt.text(0.02, 0.92,
             "Путь задержки / Latency path:\nДатчик→Fog→Курьер→Телефон\nSensor→Fog→Courier→Phone",
             transform=plt.gca().transAxes, fontsize=9, va='top')
    plt.tight_layout()
    plt.show()

    # Plot 2: phone buffer over arrivals (RU/EN)
    plt.figure(figsize=(8, 4.5))
    plt.plot(range(1, len(buffer_sizes)+1), buffer_sizes, marker='s')
    plt.title("Буфер телефона по задачам / Phone Buffer Size over Tasks")
    plt.xlabel("Порядок прибытия задач / Arrival order (Task #)")
    plt.ylabel("Сообщений в буфере / Messages in buffer")
    plt.tight_layout()
    plt.show()

def main():
    latencies, buffer_sizes, avg_latency, p95 = simulate()

    # Console output in RU and EN
    print("=== Метрики (RU) ===")
    print(f"Конвейер: {PIPELINE_RU}")
    print(f"Средняя сквозная задержка (мс): {avg_latency:.2f}")
    print(f"~95-й перцентиль задержки (мс): {p95:.2f}")

    # print("\n=== Metrics (EN) ===")
    # print(f"Pipeline: {PIPELINE_EN}")
    # print(f"Average end-to-end latency (ms): {avg_latency:.2f}")
    # print(f"~95th percentile latency (ms): {p95:.2f}")

    plot(latencies, buffer_sizes)

if __name__ == '__main__':
    main()
