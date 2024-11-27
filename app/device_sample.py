from core.services.device_control.lin_device_controller import LinDeviceController, LinUserInfo
from core.services.device_control.win_device_controller import WinDeviceController, WinUserInfo


def get_device_info(ip_address):
    ssh_error = None
    win_rm_error = None
    try:
        lin_controller = LinDeviceController(ip_address, LinUserInfo)
        print("Попытка подключения по SSH...")
        device_info = lin_controller.get_info()
        if device_info:
            print("Информация получена по SSH.")
            return device_info
        else:
            print("Не удалось получить информацию по SSH.")
    except Exception as e:
        print(f"SSH: {e} Exception")
        ssh_error = f"{e} Exception"

    try:
        win_controller = WinDeviceController(ip_address, WinUserInfo)
        print("Попытка подключения по WinRM...")
        device_info = win_controller.get_info()
        if device_info:
            print("Информация получена по WinRM.")
            return device_info
        else:
            print("Не удалось получить информацию по WinRM.")
    except Exception as e:
        print(f"WinRM: {e} Exception")
        win_rm_error = f"{e} Exception"
    if ssh_error and win_rm_error:
        raise Exception(f"Errors:\nSSH: {ssh_error}\nWinRM: {win_rm_error}")
