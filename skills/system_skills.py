import psutil

def check_system_status():
    """Checks CPU, Memory, and Battery status and returns alerts."""
    alerts = []
    
    # Check Battery
    try:
        battery = psutil.sensors_battery()
        if battery and not battery.power_plugged and battery.percent < 25:
            alerts.append(f"Warning: Battery is low at {battery.percent} percent.")
    except Exception:
        pass # Fails on desktops without batteries

    # Check CPU
    cpu_usage = psutil.cpu_percent(interval=1)
    if cpu_usage > 90:
        alerts.append(f"High CPU Alert: Usage is at {cpu_usage} percent.")
        
    # Check Memory
    memory_usage = psutil.virtual_memory().percent
    if memory_usage > 85:
        alerts.append(f"High Memory Alert: RAM usage is at {memory_usage} percent.")
        
    return alerts