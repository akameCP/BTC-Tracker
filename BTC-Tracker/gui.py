from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QApplication
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from data import BtcGraphData
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import talib
import asyncio

class HomePage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('BTC Tracker')
        self.setGeometry(200, 200, 1000, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        self.btc_panel = BtcChart()
        self.layout.addWidget(self.btc_panel)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.start_data_loader)
        self.timer.start(30000)
        self.start_data_loader()

    def start_data_loader(self):
        self.data_loader = DataLoader()
        self.data_loader.btc_data_signal.connect(self.btc_panel.update_chart)
        self.data_loader.start()

class BtcChart(QWidget):
    def __init__(self):
        super().__init__()
        self.chart_widget = BtcChartLoad()
        layout = QVBoxLayout(self)
        layout.addWidget(self.chart_widget)
        self.setLayout(layout)
    
    def update_chart(self, prices):
        self.chart_widget.update_price(prices)

        self.ind_thread = IndicatorCalculator(prices)
        self.ind_thread.result_signal.connect(self.chart_widget.update_indicators)
        self.ind_thread.start()

class BtcChartLoad(FigureCanvas):
    def __init__(self):
        self.fig, self.axs = plt.subplots(3, 1, figsize=(10, 6))
        super().__init__(self.fig)

        self.fig.patch.set_facecolor('black')

        for ax in self.axs:
            ax.set_facecolor('black')
            ax.grid(True, color='gray', linestyle='--', alpha=0.3)
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            ax.title.set_color('white')

        self.price_line, = self.axs[0].plot([], [], color='cyan', label='BTC Close')
        self.ema_fast_line, = self.axs[0].plot([], [], color='orange', label='EMA 10')
        self.ema_slow_line, = self.axs[0].plot([], [], color='red', label='EMA 30')
        self.axs[0].legend(facecolor='black', edgecolor='white', labelcolor='white')

        self.macd_line, = self.axs[1].plot([], [], color='cyan', label='MACD')
        self.macdsignal_line, = self.axs[1].plot([], [], color='magenta', label='Signal')
        self.axs[1].legend(facecolor='black', edgecolor='white', labelcolor='white')

        self.rsi_line, = self.axs[2].plot([], [], color='purple', label='RSI')
        self.axs[2].axhline(70, color='red', linestyle='--')
        self.axs[2].axhline(30, color='green', linestyle='--')
        self.axs[2].legend(facecolor='black', edgecolor='white', labelcolor='white')

        self.fig.tight_layout()

    def update_price(self, prices):
        self.price_line.set_data(np.arange(len(prices)), prices)
        self.axs[0].relim()
        self.axs[0].autoscale_view()
        self.draw()

    def update_indicators(self, indicators):
        if "ema_fast" in indicators:
            self.ema_fast_line.set_data(np.arange(len(indicators["ema_fast"])), indicators["ema_fast"])
        if "ema_slow" in indicators:
            self.ema_slow_line.set_data(np.arange(len(indicators["ema_slow"])), indicators["ema_slow"])
            self.axs[0].relim()
            self.axs[0].autoscale_view()

        if "macd" in indicators:
            self.axs[1].clear()
            self.axs[1].plot(indicators["macd"], color='cyan', label='MACD')
            self.axs[1].plot(indicators["macdsignal"], color='magenta', label='Signal')
            self.axs[1].bar(np.arange(len(indicators["macdhist"])), indicators["macdhist"], color='gray', alpha=0.5)
            self.axs[1].set_facecolor('black')
            self.axs[1].grid(True, color='gray', linestyle='--', alpha=0.3)
            self.axs[1].tick_params(axis='x', colors='white')
            self.axs[1].tick_params(axis='y', colors='white')
            self.axs[1].set_title("MACD", color='white')
            self.axs[1].legend(facecolor='black', edgecolor='white', labelcolor='white')

        if "rsi" in indicators:
            self.axs[2].clear()
            self.axs[2].plot(indicators["rsi"], color='purple', label='RSI')
            self.axs[2].axhline(70, color='red', linestyle='--')
            self.axs[2].axhline(30, color='green', linestyle='--')
            self.axs[2].set_facecolor('black')
            self.axs[2].grid(True, color='gray', linestyle='--', alpha=0.3)
            self.axs[2].tick_params(axis='x', colors='white')
            self.axs[2].tick_params(axis='y', colors='white')
            self.axs[2].set_title("RSI", color='white')
            self.axs[2].legend(facecolor='black', edgecolor='white', labelcolor='white')

        self.fig.tight_layout()
        self.draw()

class IndicatorCalculator(QThread):
    result_signal = pyqtSignal(dict)

    def __init__(self, data):
        super().__init__()
        self.data = data

    def run(self):
        ema_fast = talib.EMA(self.data, timeperiod=10)
        ema_slow = talib.EMA(self.data, timeperiod=30)
        self.result_signal.emit({"ema_fast": ema_fast, "ema_slow": ema_slow})
        self.msleep(50)

        macd, macdsignal, macdhist = talib.MACD(self.data)
        self.result_signal.emit({"macd": macd, "macdsignal": macdsignal, "macdhist": macdhist})
        self.msleep(50)

        rsi = talib.RSI(self.data, timeperiod=14)
        self.result_signal.emit({"rsi": rsi})

class DataLoader(QThread):
    btc_data_signal = pyqtSignal(np.ndarray)
    
    def run(self):
        asyncio.run(self.load_data())
    
    async def load_data(self):
        btc_data = BtcGraphData()
        btc_prices = btc_data.run()  
        self.btc_data_signal.emit(np.array(btc_prices))

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = HomePage()
    window.show()
    sys.exit(app.exec_())
