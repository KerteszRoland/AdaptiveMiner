from infi.systray import SysTrayIcon
from time import sleep
import psutil
from subprocess import CREATE_NO_WINDOW
import os
import signal
from pathlib import Path
import webbrowser
import winshell
from dotenv import load_dotenv
import keyboard


load_dotenv()


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


class Miner:
    def __init__(self, miner_path, tray):
        self.miner_path = Path(miner_path)
        self.miner_proc = None
        self.is_paused = False
        self.terminated = False
        self.tray = tray

    def start(self):
        if self.miner_proc == None and not self.is_paused:
            command = [f"{self.miner_path}"]
            self.miner_proc = psutil.Popen(
                command, stdout=None, shell=True, creationflags=CREATE_NO_WINDOW)
            print("---Started Miner---")
            self.tray.update(icon="icons/pickaxe_on.ico")
            keyboard.press_and_release('ctrl+shift+alt+k')

    def stop(self):
        if self.miner_proc != None:
            kill_proc_tree(self.miner_proc.pid)
            self.miner_proc = None
            print("---Stopped Miner---")
            self.tray.update(icon="icons/pickaxe_off.ico")
            keyboard.press_and_release('ctrl+shift+alt+l')

    def pause(self):
        self.is_paused = True
        self.stop()
        print("---Paused Miner---")
        self.tray.update(icon="icons/pickaxe_pause.ico")

    def resume(self):
        self.is_paused = False


def main():
    def tray_run_at_startup(tray):
        path = fr"C:\Users\{os.getlogin()}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\AdaptiveMiner.lnk"
        name = "main.pyw"
        this_file_path = os.path.join(os.path.abspath('.'), name)
        winshell.CreateShortcut(path, this_file_path, Arguments="", StartIn=os.path.abspath(
            '.'), Icon=(os.path.abspath('./icons/pickaxe.ico'), 0), Description="AdaptiveMinerBat")

    def tray_stop_miner(tray):
        miner.pause()

    def tray_start_miner(tray):
        miner.resume()

    def tray_quit(tray):
        miner.pause()
        miner.terminated = True

    def tray_open_stats(tray):
        webbrowser.open_new(os.environ.get("DASHBOARD"))

    menu_options = (("Start miner", None, tray_start_miner), ("Stop miner",
                    None, tray_stop_miner), ("Statistics", None, tray_open_stats), ("Run at Startup", None, tray_run_at_startup))
    systray = SysTrayIcon("icons/pickaxe.ico", "AdaptiveMiner",
                          menu_options, on_quit=tray_quit)
    systray.start()

    check_freq = os.environ.get("CHECK_FREQ")
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
                sleep(check_freq)
    except Exception as e:
        miner.pause()
        systray.shutdown()
        raise e


if __name__ == "__main__":
    main()
    exit()
