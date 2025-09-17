# BTC Tracker

The **BTC Tracker** project implements a real-time Bitcoin price visualization and analysis system using **CCXT** for fetching live price data. It offers a graphical user interface (GUI) built with **PyQt5** and displays price charts along with technical indicators such as EMA, MACD, and RSI.

---

## Features

- **Real-Time BTC Chart:** Displays live BTC/USDT closing prices.  
- **Technical Indicators:** EMA (fast and slow), MACD (with signal and histogram), and RSI.  
- **Dynamic Charts:** Updates automatically every 30 seconds.  
- **Interactive GUI:** Built with PyQt5 for smooth user experience.  

---

## Technologies Used

- **Python:** Main programming language.  
- **PyQt5:** For creating the GUI.  
- **Matplotlib:** For plotting price and indicator charts.  
- **TA-Lib:** For calculating EMA, MACD, and RSI indicators.  
- **CCXT:** For fetching live cryptocurrency data.  
- **NumPy & Pandas:** For data processing and numerical computations.  

---

## Running the Application

To start the project, run the `gui.py` script:

```bash
python gui.py
