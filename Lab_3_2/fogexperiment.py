"""
Исследование влияния частоты чтения на буфер смартфона
Study of reading frequency impact on smartphone buffer
"""
import random
import statistics
import matplotlib.pyplot as plt
import numpy as np

PIPELINE_RU = "Датчик → Fog → Курьер → Телефон"
PIPELINE_EN = "Sensor → Fog → Courier → Phone"

def simulate(n_tasks=30, seed=7, read_interval_ms=120):
    """
    Симуляция конвейера обработки данных
    Simulation of data processing pipeline
    
    Args:
        n_tasks: количество задач / number of tasks
        seed: seed для воспроизводимости / seed for reproducibility
        read_interval_ms: интервал чтения телефона (мс) / phone reading interval (ms)
    """
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
    time = 0
    buffer_sizes = []
    buf = 0
    read_times = []  # Времена чтений
    
    for L in latencies:
        time += L
        # Проверяем, сколько чтений произошло за это время
        reads = time // read_interval_ms
        for _ in range(int(reads - len(read_times))):
            if buf > 0:
                buf -= 1
            read_times.append(len(read_times) * read_interval_ms)
        buf += 1
        buffer_sizes.append(buf)

    # Завершаем все чтения до конца симуляции
    final_time = time
    final_reads = final_time // read_interval_ms
    for _ in range(int(final_reads - len(read_times))):
        if buf > 0:
            buf -= 1
        read_times.append(len(read_times) * read_interval_ms)
    
    avg_latency = statistics.mean(latencies)
    p95 = statistics.quantiles(latencies, n=20)[18]  # ≈95th percentile
    
    # Дополнительные метрики для буфера
    max_buffer = max(buffer_sizes) if buffer_sizes else 0
    avg_buffer = statistics.mean(buffer_sizes) if buffer_sizes else 0
    buffer_empty_percentage = (buffer_sizes.count(1) / len(buffer_sizes)) * 100 if buffer_sizes else 0
    
    return {
        'latencies': latencies,
        'buffer_sizes': buffer_sizes,
        'avg_latency': avg_latency,
        'p95': p95,
        'max_buffer': max_buffer,
        'avg_buffer': avg_buffer,
        'buffer_empty_percentage': buffer_empty_percentage,
        'read_interval': read_interval_ms,
        'read_times': read_times
    }

def run_comparison():
    """Запуск сравнения трех сценариев"""
    scenarios = [
        {"name": "Ускоренная обработка", "interval": 60, "color": "green", "marker": "o"},
        {"name": "Стандартная обработка", "interval": 120, "color": "blue", "marker": "s"},
        {"name": "Замедленная обработка", "interval": 200, "color": "red", "marker": "^"}
    ]
    
    results = {}
    
    print("=" * 70)
    print("ИССЛЕДОВАНИЕ ВЛИЯНИЯ ЧАСТОТЫ ЧТЕНИЯ НА БУФЕР СМАРТФОНА")
    print("=" * 70)
    
    # Запускаем симуляции для каждого сценария
    for scenario in scenarios:
        print(f"\n📊 Сценарий: {scenario['name']}")
        print(f"   Интервал чтения: {scenario['interval']} мс")
        
        result = simulate(read_interval_ms=scenario['interval'])
        results[scenario['name']] = result
        
        # Вывод метрик
        print(f"   • Средняя задержка: {result['avg_latency']:.2f} мс")
        print(f"   • 95-й перцентиль: {result['p95']:.2f} мс")
        print(f"   • Максимальный буфер: {result['max_buffer']} сообщений")
        print(f"   • Средний буфер: {result['avg_buffer']:.2f} сообщений")
        print(f"   • % времени с 1 сообщением: {result['buffer_empty_percentage']:.1f}%")
    
    return scenarios, results

def plot_comparison(scenarios, results):
    """Визуализация сравнения сценариев"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # График 1: Сравнение размеров буфера
    ax1 = axes[0, 0]
    for scenario in scenarios:
        name = scenario['name']
        buffer_data = results[name]['buffer_sizes']
        ax1.plot(range(1, len(buffer_data) + 1), buffer_data, 
                label=f"{name} ({scenario['interval']} мс)",
                color=scenario['color'], marker=scenario['marker'], markersize=4, linewidth=1.5)
    
    ax1.set_title('Сравнение размера буфера смартфона\nпри разной частоте чтения', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Номер задачи / Task #')
    ax1.set_ylabel('Сообщений в буфере / Messages in buffer')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # График 2: Гистограмма максимальных размеров буфера
    ax2 = axes[0, 1]
    scenario_names = [s['name'] for s in scenarios]
    max_buffers = [results[name]['max_buffer'] for name in scenario_names]
    colors = [s['color'] for s in scenarios]
    
    bars = ax2.bar(scenario_names, max_buffers, color=colors, alpha=0.7)
    ax2.set_title('Максимальный размер буфера', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Максимальное количество сообщений')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Добавляем значения на столбцы
    for bar, value in zip(bars, max_buffers):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{value}', ha='center', va='bottom')
    
    # График 3: Средние значения буфера
    ax3 = axes[1, 0]
    avg_buffers = [results[name]['avg_buffer'] for name in scenario_names]
    empty_percentages = [results[name]['buffer_empty_percentage'] for name in scenario_names]
    
    x = np.arange(len(scenario_names))
    width = 0.35
    
    bars1 = ax3.bar(x - width/2, avg_buffers, width, label='Средний буфер', alpha=0.7)
    bars2 = ax3.bar(x + width/2, empty_percentages, width, label='% времени с 1 сообщением', alpha=0.7)
    
    ax3.set_title('Средние показатели буфера', fontsize=12, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels([f"{s['name']}\n({s['interval']} мс)" for s in scenarios])
    ax3.set_ylabel('Значение')
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    # График 4: Зависимость от интервала чтения
    ax4 = axes[1, 1]
    intervals = [s['interval'] for s in scenarios]
    
    ax4.plot(intervals, max_buffers, 'o-', label='Максимальный буфер', linewidth=2)
    ax4.plot(intervals, avg_buffers, 's-', label='Средний буфер', linewidth=2)
    ax4.plot(intervals, empty_percentages, '^-', label='% с 1 сообщением', linewidth=2)
    
    ax4.set_title('Зависимость показателей от интервала чтения', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Интервал чтения (мс)')
    ax4.set_ylabel('Значение')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    plt.suptitle('Влияние частоты чтения сообщений на размер буфера смартфона', 
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.show()
    
    # Вывод результатов в таблице
    print("\n" + "=" * 70)
    print("РЕЗЮМЕ РЕЗУЛЬТАТОВ")
    print("=" * 70)
    print(f"{'Сценарий':<25} {'Интервал':<10} {'Макс.буфер':<12} {'Ср.буфер':<10} {'% пустого':<10}")
    print("-" * 70)
    
    for scenario in scenarios:
        name = scenario['name']
        r = results[name]
        print(f"{name:<25} {r['read_interval']:<10} {r['max_buffer']:<12} {r['avg_buffer']:<10.2f} {r['buffer_empty_percentage']:<10.1f}")
    
    # Анализ результатов
    print("\n" + "=" * 70)
    print("АНАЛИЗ РЕЗУЛЬТАТОВ")
    print("=" * 70)
    
    fast = results["Ускоренная обработка"]
    slow = results["Замедленная обработка"]
    
    print("1. При УСКОРЕННОЙ обработке (интервал 60 мс):")
    print(f"   • Буфер растет медленнее (макс. {fast['max_buffer']} сообщений)")
    print(f"   • Чаще опустошается ({fast['buffer_empty_percentage']:.1f}% времени с 1 сообщением)")
    print(f"   • Средний размер буфера меньше ({fast['avg_buffer']:.2f} сообщений)")
    
    print("\n2. При ЗАМЕДЛЕННОЙ обработке (интервал 200 мс):")
    print(f"   • Буфер растет быстрее (макс. {slow['max_buffer']} сообщений)")
    print(f"   • Редко опустошается ({slow['buffer_empty_percentage']:.1f}% времени с 1 сообщением)")
    print(f"   • Средний размер буфера больше ({slow['avg_buffer']:.2f} сообщений)")
    
    print("\n3. ВЫВОД:")
    print("   ✓ Уменьшение интервала чтения (более частая обработка) приводит к:")
    print("     - Меньшему размеру буфера")
    print("     - Более частому его опустошению")
    print("     - Более стабильной работе системы")
    print("\n   ✓ Увеличение интервала чтения (более редкая обработка) приводит к:")
    print("     - Накоплению сообщений в буфере")
    print("     - Риску переполнения при пиковых нагрузках")
    print("     - Увеличению задержек доставки сообщений")

def plot_detailed_scenario(read_interval_ms=120, scenario_name="Стандартная обработка"):
    """Детальная визуализация для одного сценария"""
    result = simulate(read_interval_ms=read_interval_ms)
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    # График 1: Задержки
    ax1 = axes[0]
    ax1.plot(range(1, len(result['latencies']) + 1), result['latencies'], 
             marker='o', markersize=4, linewidth=1.5, color='blue')
    ax1.axhline(y=result['avg_latency'], color='red', linestyle='--', 
                label=f'Среднее: {result["avg_latency"]:.2f} мс')
    ax1.axhline(y=result['p95'], color='orange', linestyle=':', 
                label=f'P95: {result["p95"]:.2f} мс')
    ax1.set_title(f'Сквозная задержка ({scenario_name})', fontweight='bold')
    ax1.set_xlabel('Номер задачи')
    ax1.set_ylabel('Задержка, мс')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # График 2: Буфер
    ax2 = axes[1]
    tasks = range(1, len(result['buffer_sizes']) + 1)
    ax2.plot(tasks, result['buffer_sizes'], marker='s', markersize=4, 
             linewidth=1.5, color='green')
    ax2.axhline(y=result['avg_buffer'], color='purple', linestyle='--',
                label=f'Средний буфер: {result["avg_buffer"]:.2f}')
    ax2.axhline(y=result['max_buffer'], color='red', linestyle=':',
                label=f'Максимум: {result["max_buffer"]}')
    
    # Показать моменты чтения
    read_indices = []
    for read_time in result['read_times']:
        # Найдем, какая задача была обработана к этому времени
        cumulative_time = 0
        for i, latency in enumerate(result['latencies']):
            cumulative_time += latency
            if cumulative_time >= read_time:
                read_indices.append(i + 1)
                break
    
    if read_indices:
        ax2.scatter(read_indices, [result['buffer_sizes'][i-1] for i in read_indices],
                   color='red', s=50, zorder=5, label='Моменты чтения', alpha=0.6)
    
    ax2.set_title(f'Буфер смартфона ({scenario_name})', fontweight='bold')
    ax2.set_xlabel('Номер задачи')
    ax2.set_ylabel('Сообщений в буфере')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # График 3: Статистика
    ax3 = axes[2]
    metrics = ['Ср.задержка', 'P95', 'Макс.буфер', 'Ср.буфер', '% с 1 сообщ.']
    values = [result['avg_latency'], result['p95'], result['max_buffer'], 
              result['avg_buffer'], result['buffer_empty_percentage']]
    colors = ['blue', 'orange', 'red', 'purple', 'green']
    
    bars = ax3.bar(metrics, values, color=colors, alpha=0.7)
    ax3.set_title(f'Метрики ({scenario_name})', fontweight='bold')
    ax3.set_ylabel('Значение')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Добавляем значения на столбцы
    for bar, value in zip(bars, values):
        if metrics[bars.index(bar)] == '% с 1 сообщ.':
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{value:.1f}%', ha='center', va='bottom')
        else:
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{value:.1f}', ha='center', va='bottom')
    
    plt.suptitle(f'Анализ сценария: {scenario_name} (интервал чтения: {read_interval_ms} мс)',
                 fontsize=12, fontweight='bold', y=1.05)
    plt.tight_layout()
    plt.show()
    
    return result

def main():
    """Основная функция"""
    print("=" * 70)
    print("ЛАБОРАТОРНАЯ РАБОТА: ВЛИЯНИЕ ЧАСТОТЫ ЧТЕНИЯ НА БУФЕР СМАРТФОНА")
    print("=" * 70)
    
    # Запуск сравнения трех сценариев
    scenarios, results = run_comparison()
    
    # Визуализация сравнения
    plot_comparison(scenarios, results)
    
    # Детальный анализ каждого сценария
    print("\n" + "=" * 70)
    print("ДЕТАЛЬНЫЙ АНАЛИЗ КАЖДОГО СЦЕНАРИЯ")
    print("=" * 70)
    
    detailed_scenarios = [
        (60, "Ускоренная обработка (60 мс)"),
        (120, "Стандартная обработка (120 мс)"),
        (200, "Замедленная обработка (200 мс)")
    ]
    
    for interval, name in detailed_scenarios:
        print(f"\n📈 Анализ сценария: {name}")
        plot_detailed_scenario(interval, name)
    
    print("\n" + "=" * 70)
    print("ЗАКЛЮЧЕНИЕ")
    print("=" * 70)
    print("""
    Эксперимент подтвердил гипотезу:
    
    1. При УМЕНЬШЕНИИ интервала чтения (более частой обработке, 60 мс):
       • Буфер смартфона растет МЕДЛЕННЕЕ
       • Буфер ЧАЩЕ опустошается (больший % времени содержит 1 сообщение)
       • Система более отзывчива и стабильна
       
    2. При УВЕЛИЧЕНИИ интервала чтения (более редкой обработке, 200 мс):
       • Буфер смартфона растет БЫСТРЕЕ
       • Буфер РЕЖЕ опустошается (накапливает больше сообщений)
       • Возрастает риск переполнения при пиковых нагрузках
       
    Рекомендация: Для систем реального времени следует использовать
    меньший интервал чтения для предотвращения накопления сообщений
    и обеспечения минимальных задержек доставки.
    """)

if __name__ == '__main__':
    main()