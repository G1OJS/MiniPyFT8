import tkinter as tk
from tkinter import ttk
import time, threading, socket, queue
from MiniPyFT8.receiver import Receiver
from MiniPyFT8.transmitter import Transmitter
MAX_TX_START_CYCLETIME = 3

class App:
    def __init__(self, root):
        self.call_hashes = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 2121))
        self.rx = Receiver()
        self.tx = Transmitter(self.rx.get_call_hashes, self.rx.add_call_hashes)
        self.decode_queue = queue.Queue()
        self.root = root
        self.container = ttk.Frame(self.root) 
        self.scrollbar = ttk.Scrollbar(self.container)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget = tk.Text(self.container, wrap=tk.WORD, yscrollcommand=self.scrollbar.set)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.text_widget.tag_config('to_me', foreground = 'white', background = 'red', font=('Helvetica', 12, 'bold'))
        self.text_widget.tag_config('cq', foreground = 'white', background = 'green', font=('Helvetica', 12, 'bold'))
        self.text_widget.tag_config('norm', foreground = 'black', background = 'white', font=('Helvetica', 12))
        self.text_widget.tag_config('qso', foreground = 'white', background = 'blue', font=('Helvetica', 12))
        self.text_widget.bind('<Button-1>', self.row_click)

        self.scrollbar.config(command=self.text_widget.yview)
        self.container.pack() 
        self.root.bind("<<received_decode>>", self.received_decode)
        threading.Thread(target = self.monitor_socket, daemon = True).start()

    def add_call_hashes(self, call):
        chars = " 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ/"
        call_padded = (call + "          ")[:11]
        hashes = []
        for m in [10,12,22]:
            x = 0
            for c in call_padded:
                x = 38*x + chars.find(c)
                x = x & ((int(1) << 64) - 1)
            x = x & ((1 << 64) - 1)
            x = x * 47055833459
            x = x & ((1 << 64) - 1)
            x = x >> (64 - m)
            hashes.append(x)
            self.call_hashes[(x, m)] = call
        return hashes

    def row_click(self, e):
        curr = e.widget.index("current").split('.')[0]
        print(e.widget.get(f"{curr}.0", f"{curr}.end"))
        self.tx.set_transmit_payload("CQ G1OJS IO90")

    def monitor_socket(self):
        while True:
            time.sleep(0.1)
            decode_text, addres = self.sock.recvfrom(1024)
            decode_text = decode_text.decode()
            if decode_text:
                if decode_text.startswith('fHz'):
                    decode_text = ' '.join(decode_text.split(',')[5:])
                self.decode_queue.put(f"{decode_text}\n")
                self.root.after(0, lambda: self.root.event_generate("<<received_decode>>"))

    def received_decode(self, e):
        text = self.decode_queue.get()
        mtype = 'norm'
        mtype = 'cq' if 'CQ' in text else ('qso' if not '==' in text else mtype)
        self.text_widget.insert(tk.END, text, mtype)
        self.text_widget.see('end')

app = App(tk.Tk())
app.root.mainloop()
