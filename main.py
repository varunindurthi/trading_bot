import tkinter as tk
import logging
from bitmex_futures import get_contracts


logger = logging.getLogger()

logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)   

file_handler = logging.FileHandler('info.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)


logger.addHandler(stream_handler)
logger.addHandler(file_handler)



if __name__ == '__main__':  

    bitmex_contracts = get_contracts() 
    
    root = tk.Tk()

    i = 0
    j = 0

    for contract in bitmex_contracts:
        label_widget = tk.Label(root,text=contract)
        label_widget.grid(row=i,column=j)
        
        if i==4:
            j +=1
            i = 0
        else:
            i +=1



    root.mainloop()
