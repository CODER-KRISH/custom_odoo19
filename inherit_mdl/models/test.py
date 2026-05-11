def float_to_time(hours):
    hours = float(hours or 0)

    total_minutes = round(hours * 60)
    h = total_minutes // 60
    m = total_minutes % 60

    return f"{int(h):02d}:{int(m):02d}"


print(float_to_time(0.50))  # 00:50
print(float_to_time(1))  # 00:50
print(float_to_time("0.83"))  # 00:50
print(float_to_time(False))  # 00:00
print(float_to_time(None))  # 00:00
