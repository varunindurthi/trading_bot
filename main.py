import tkinter as tk
import logging
from connectors.binance_futures import BinanceFuturesClient
from config import credentials


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

    binance = BinanceFuturesClient(credentials()[0], credentials()[1] ,True)

           
    root = tk.Tk()
    root.configure(bg='gray12')

    
    root.mainloop()
