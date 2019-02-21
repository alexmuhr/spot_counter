# spot_counter
This is a program that is designed to identify, count, and classify spots in an image. Intended usage is to classify material defects apparent in an image. Program outputs a histogram of spot count by area, an image that is a resized version of the original with spots circled, and an excel summary report. The summary report is also displayed in the GUI textbox.

spot_counter.py defines the frontend GUI
spot_counter_backend.py defines the backend function that loads the image, identifies spots, and creates outputs. This must be in the same directory as spot_counter.py
spot_counter.exe is an executable that combines both spot_counter.py and spot_counter_backend.py 

Spots should be dark on a light background, however some simple modification of the backend function could change the program to pick out light spots on a dark background instead.

The program assumes a 4800 dpi image and determines mm2 size of spots based on this assumption. The program also uses the 4800 dpi assumption to crop a 45 mm diameter analysis area from the input image file. The program could be adopted for different pixel resolutions, output units, or analysis area crops with some simple modification to the backend function.

Modifications to the backend function can also be used to adopt the format of the output histogram and excel summary report.

In the future I may add options to the GUI interface that would dynamically modify the backend function in order to make the program more flexible.
