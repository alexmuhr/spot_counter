from tkinter import *
from tkinter import filedialog
import spot_counter_backend
import pywt._extensions._cwt

def browse_command():
    # Allow user to select a directory and store it in global var
    # called folder_path
    global file_path
    global filename
    filename = filedialog.askopenfilename(title = 'Select Image File',
        filetypes = [("tif files","*.tif"), ("jpeg files","*.jpg")])
    text1.delete('1.0', END)
    text1.insert('1.0', filename)

def scan_command():
    text2.delete('1.0', END)
    success, scan_out = spot_counter_backend.spot_scan(filename)
    if success == 0:
        text2.insert('1.0', "Scan Success!\n")
        for ind in scan_out.index.values:
            text2.insert(END, str([ind]+list(scan_out.loc[ind,:].values)) + '\n')
    else:
        text2.insert(END, scan_out)

window = Tk()

b1 = Button(window, text = "Browse", width = 12, command = browse_command)
b1.grid(row = 0, column = 0)

text1 = Text(window, height = 1, width = 60)
text1.grid(row = 0, column = 1)

b2 = Button(window, text = "Scan", width = 12, command = scan_command)
b2.grid(row = 0, column = 2)

b3 = Button(window, text = "Close", width = 12, command = window.quit)
b3.grid(row = 0, column = 3)

text2 = Text(window, height = 6, width = 100)
text2.grid(row = 2, column = 0, columnspan = 4)

window.mainloop()
