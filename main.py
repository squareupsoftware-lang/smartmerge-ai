import sys
import os
import threading
import uvicorn

# Qt plugin fix
import PyQt5
plugin_path = os.path.join(os.path.dirname(PyQt5.__file__), "Qt5", "plugins", "platforms")
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path

from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.config import settings
from api.api_server import create_app


def run_api():
    api_app = create_app()
    uvicorn.run(api_app, host=settings.HOST, port=settings.PORT)


def load_stylesheet(app):
    with open("style.qss", "r") as f:
        app.setStyleSheet(f.read())


if __name__ == "__main__":
    # 🔥 Start API in background
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # 🎯 Start Qt App
    qt_app = QApplication(sys.argv)
    qt_app.include_router(theme_router, prefix="/api/v1/theme")
    load_stylesheet(qt_app)

    try:
        mainWindow = MainWindow()
        mainWindow.show()
    except Exception as e:
        import traceback
        print("APP CRASH:", e)
        traceback.print_exc()

    sys.exit(qt_app.exec_())