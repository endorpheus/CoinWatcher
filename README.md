![coin](https://github.com/user-attachments/assets/8bdc0635-0168-42d3-9d4d-4cdc9726f23b)
# CoinWatcher 𓆈 version 1.0
A simple crypto coin price sentinel using the free CoinGecko API 𓆈<br>

### Synopsis:
This Python application allows you to monitor the price of your favorite cryptocurrency in real-time. It sits in your system tray, updating the price at a user-defined interval and displaying it on mouse hover. Originally written for **KDE** (but should work for other desktops)

###  Features:

* Monitor the price of any cryptocurrency supported by CoinGecko API.
* User-friendly interface for easy configuration.
* Set the update interval for price information.
* View the current price on mouse hover over the system tray icon.
* Access settings and about information through the system tray menu.

Note:<br>
Prices are NOT in realtime due to the request interval range (300-1200 secs).<br>
Of course, feel free to tweak the slider range to whatever you prefer.<br>
The CoinGecko 𓆈 site indicates a ~30 requests/min limit for free accounts.<br>


###  Dependencies:

This application requires the following Python libraries to function:

* PyQt6: A powerful cross-platform GUI toolkit for Python ([https://riverbankcomputing.com/software/pyqt/intro](https://riverbankcomputing.com/software/pyqt/intro))
* requests: An elegant and simple HTTP library for Python ([https://requests.readthedocs.io/](https://requests.readthedocs.io/))

###  Installation:

1.  Make sure you have Python 3 and pip installed on your system.
2.  Open a terminal or command prompt and navigate to the directory containing the application files.
3.  Run the following command to install the required dependencies:

```bash
pip install PyQt6 requests
```

4.  Run the application using the following command:

```bash
python kde-coin-watcher.py
```

###  Usage:

* The application will minimize itself to the system tray upon launch.
* Right-click on the system tray icon to access the menu.
* Select "Settings" to open the configuration window.
    * Change the ticker symbol in the input field to track a different cryptocurrency. 
    * Use the slider to adjust the update interval (in seconds).
* Hover your mouse over the system tray icon to see the current price of the selected cryptocurrency.

### API Errors:

If you are getting errors or the app is unable to retrieve prices via the API, it is likely you have the Timer Interval set too low.  I've made a concerted effort to keep the requests 300 seconds apart by default.  You can increase the interval if you feel like your requests are being throttled or outright denied due to high traffic (which is atypical for pro/paid API users).

You shouldn't really need an API key to use this, but I'm sure CoinGecko would appreciate your support.  All that aside, this app really doesn't require much from CG and should run virtually non stop.

### Future Plans:

* I'd like to see this use a few more endpoints of the free CoinGecko API. 𓆈
* It would be fun to add a search function to browse tickers.
* A top ten movers list might be a good bit of info.
* Of course, having multiple currencies set would be handy for those diversified DCAers.
* If possible it would be great to show candle graphs.

Who knows if we'll ever get to this, but it's fun to toss around.

### Attribution:

Thanks to FlatIcon for the nice icon for the project.<br>
<a href="https://www.flaticon.com/free-icons/growth" title="growth icons">Growth icons created by Freepik - Flaticon</a>

### Thanks for dropping by! 😺
