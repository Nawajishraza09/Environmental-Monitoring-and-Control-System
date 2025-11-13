import sys
import os

from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QApplication

from ui.main_window import MainWindow  # your custom main window
from ui.splash_screen import SplashScreen

class AppLauncher:
    def __init__(self):
        self.appctxt = ApplicationContext()   # 1. Instantiate ApplicationContext
        self.app = QApplication(sys.argv)
        self.splash = SplashScreen()

    def launch_main(self):
        self.window = MainWindow()   # keeping reference to prevent garbage collection
        self.window.show()
        self.splash.finish(self.window)    # Qt to clean up splash properly
        
    def run(self):
        self.splash.start(self.launch_main)    
        exit_code = self.appctxt.app.exec()   # 2. Invoke appctxt.app.exec_()
        sys.exit(exit_code)
    
if __name__ == '__main__':
    launcher = AppLauncher()
    launcher.run()