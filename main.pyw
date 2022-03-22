import math
from infi.systray import SysTrayIcon
from time import sleep
from datetime import datetime, timedelta
import psutil
from subprocess import CREATE_NO_WINDOW
import os
import signal
from pathlib import Path
import webbrowser
import winshell
from dotenv import load_dotenv
import keyboard
import json


def kill_proc_tree(pid, sig=signal.SIGTERM, include_parent=True,
                   timeout=None, on_terminate=None):
    assert pid != os.getpid(), "won't kill myself"
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    if include_parent:
        children.append(parent)
    for p in children:
        try:
            p.send_signal(sig)
        except psutil.NoSuchProcess:
            pass
    gone, alive = psutil.wait_procs(children, timeout=timeout,
                                    callback=on_terminate)
    return (gone, alive)


def get_running_processes():
    return (p.name() for p in psutil.process_iter())


def is_process_in_processes(process_name):
    return process_name in get_running_processes()


def is_any_triggering_process_is_running(triggering_processes):
    return any(is_process_in_processes(proc) for proc in triggering_processes)


def now_time():
    return datetime.now().strftime("%d/%m - %H:%M")


class Miner:
    def __init__(self, miner_path, tray):
        self.miner_path = Path(miner_path)
        self.miner_proc = None
        self.is_paused = False
        self.terminated = False
        self.tray = tray
        self.dashboard_url = os.environ.get("DASHBOARD_URL")
        self.afterburner_miner = os.environ.get("AFTERBURNER_MINER_SHORTCUT")
        self.afterburner_idle = os.environ.get("AFTERBURNER_IDLE_SHORTCUT")
        self.mined_time = timedelta()
        self.miner_uptime = timedelta()
        self.miner_started_at = None

    def start(self):
        if self.miner_proc == None and not self.is_paused:
            self.load_mined_time()
            command = [self.miner_path]
            self.miner_proc = psutil.Popen(
                command, stdout=None, shell=True, creationflags=CREATE_NO_WINDOW)
            print("---Started Miner---", now_time())
            self.tray.update(icon="icons/pickaxe_on.ico")
            keyboard.press_and_release(self.afterburner_miner)
            self.miner_started_at = datetime.now()

    def stop(self):
        if self.miner_proc != None:
            kill_proc_tree(self.miner_proc.pid)
            self.miner_proc = None
            print("---Stopped Miner---", now_time())
            self.tray.update(icon="icons/pickaxe_off.ico",
                             hover_text="AdaptiveMiner - Stopped")
            keyboard.press_and_release(self.afterburner_idle)
            self.mined_time += self.miner_uptime
            self.save_mined_time()
            self.miner_uptime = timedelta()

    def pause(self):
        self.is_paused = True
        self.stop()
        self.tray.update(icon="icons/pickaxe_pause.ico",
                         hover_text="AdaptiveMiner - Paused")

    def resume(self):
        self.is_paused = False

    def open_dashboard(self):
        if self.dashboard_url != "" or None:
            webbrowser.open_new(self.dashboard_url)

    def refresh_miner_uptime(self):
        if self.miner_started_at != None:
            self.miner_uptime = datetime.now()-self.miner_started_at

            self.tray.update(
                hover_text=f"AdaptiveMiner - Mining\nUptime:{str(self.miner_uptime).split('.')[0]}\nTotal: {str(self.mined_time+self.miner_uptime).split('.')[0]}")

    def save_mined_time(self):
        data = {"seconds": self.mined_time.total_seconds()}
        with open("mined_time.json", "w") as f:
            json.dump(data, f)

    def load_mined_time(self):
        if "mined_time.json" in os.listdir():
            with open("mined_time.json", "r") as f:
                self.mined_time = timedelta(seconds=json.load(f)["seconds"])


def main():
    load_dotenv()
    print("---Launched AdaptiveMiner---", now_time())

    def tray_run_at_startup(tray):
        path = fr"C:\Users\{os.getlogin()}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\AdaptiveMiner.lnk"
        name = "main.pyw"
        this_file_path = os.path.join(os.path.abspath('.'), name)
        winshell.CreateShortcut(path, this_file_path, Arguments="", StartIn=os.path.abspath(
            '.'), Icon=(os.path.abspath('./icons/pickaxe.ico'), 0), Description="AdaptiveMinerBat")

    def tray_pause_miner(tray):
        miner.pause()

    def tray_resume_miner(tray):
        miner.resume()

    def tray_quit(tray):
        miner.pause()
        miner.terminated = True

    def tray_open_dashboard(tray):
        miner.open_dashboard()

    menu_options = [("Resume miner", None, tray_resume_miner), ("Pause miner",
                    None, tray_pause_miner), ("Run at Startup", None, tray_run_at_startup)]
    if os.environ.get("DASHBOARD_URL") != "" or None:
        menu_options.insert(2, ("Miner Dashboard", None, tray_open_dashboard))
    menu_options = tuple(menu_options)
    systray = SysTrayIcon("icons/pickaxe.ico", "AdaptiveMiner",
                          menu_options, on_quit=tray_quit)
    systray.start()

    check_freq = int(os.environ.get("CHECK_FREQ"))
    triggering_processes = os.environ.get("EXES").split(";")
    miner = Miner(
        fr"{os.environ.get('MINER_PATH')}", systray)

    try:
        while(not miner.terminated):
            if not miner.is_paused:
                if is_any_triggering_process_is_running(triggering_processes):
                    miner.stop()
                else:
                    miner.start()
                    miner.refresh_miner_uptime()
                sleep(check_freq)
    except Exception as e:
        miner.pause()
        systray.shutdown()
        raise e


if __name__ == "__main__":
    main()
    exit()
