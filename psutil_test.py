import psutil

# scputimes(user=2896.71, nice=34.08, system=1442.85, idle=138755.25, iowait=38.19, irq=0.0, softirq=118.42, steal=0.0, guest=0.0, guest_nice=0.0)
# print(psutil.cpu_times())
# [3.5, 2.1, 0.5, 4.1]
# print(psutil.cpu_percent(interval=1, percpu=True))

# print(psutil.virtual_memory())

# print(psutil.disk_partitions())

print(psutil.net_io_counters(pernic=True))