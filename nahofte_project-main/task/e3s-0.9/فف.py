from collections import defaultdict

# مسیر فایل TGFF
filename = "auto-indust-mocsyn.tgff"

# داده خام: [نوع هسته][شناسه تسک] = زمان اجرا
exec_times = defaultdict(dict)

with open(filename) as f:
    current_type = None
    for line in f:
        line = line.strip()
        if line.startswith("@RESOURCE_TYPE"):
            current_type = int(line.split()[1])
        elif line.startswith("@EXECUTION_TIME"):
            task_id, time = map(int, line.split()[1:])
            exec_times[current_type][task_id] = time

# ساخت ماتریس X: [task_id][core_type]
task_ids = sorted(set(k for d in exec_times.values() for k in d))
type_ids = sorted(exec_times.keys())

X = [[exec_times[core_type][task_id] for core_type in type_ids] for task_id in task_ids]

# چاپ خروجی
print(f"تعداد تسک‌ها: {len(X)}")
print(f"تعداد نوع‌هسته‌ها: {len(type_ids)}")
print("\nنمونه‌ای از ماتریس X (زمان اجرای تسک‌ها):")
for i, row in enumerate(X[:5]):  # فقط ۵ تسک اول برای نمونه
    print(f"تسک {i}: {row}")
