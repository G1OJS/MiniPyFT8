import tkinter as tk
from tkinter import ttk
import time, threading, socket, queue
from MiniPyFT8.receiver import Receiver
from MiniPyFT8.transmitter import Transmitter
from MiniPyFT8.rigctrl import Rig_hamlib

MAX_TX_START_CYCLETIME = 3

myCall, myGrid = "G1OJS", "IO90"

def determine_reply(rx_message, their_snr):
    if rx_message == '':
        return f"CQ {myCall} {myGrid}"
    else:
        hail, their_call, grid_rpt = rx_message.split(' ')
        
    if hail.startswith("CQ"):
        reply = f"{their_call} {myCall} {myGrid[:4]}"   
    elif hail.startswith(myCall):
        reply = f"{their_call} {myCall} {their_snr}"
        if any([m for m in ['+','-'] if m in grid_rpt]):
            reply = f"{their_call} {myCall} R{their_snr}"
        if any([m for m in ['R+','R-','RRR'] if m in grid_rpt]):
            reply = f"{their_call} {myCall} RR73"
        if grid_rpt == 'RR73':
            reply = f"{their_call} {myCall} 73"
    return reply

class App:
    def __init__(self, root):
        self.call_hashes = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 2121))
        self.rig = Rig_hamlib()
        self.rx = Receiver()
        self.tx = Transmitter(self.rx.get_call_hashes, self.rx.add_call_hashes, self.rig)
        self.decode_queue = queue.Queue()
        self.root = root
        self.container = ttk.Frame(self.root) 
        self.scrollbar = ttk.Scrollbar(self.container)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget = tk.Text(self.container, wrap=tk.WORD, yscrollcommand=self.scrollbar.set)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.text_widget.tag_config('norm', foreground = 'white', background = 'blue', font=('Helvetica', 12))
        self.text_widget.tag_config('info', foreground = 'black', background = 'white', font=('Helvetica', 12))
        self.text_widget.tag_config('cq', foreground = 'white', background = 'green', font=('Helvetica', 12, 'bold'))
        self.text_widget.tag_config('to_me', foreground = 'white', background = 'red', font=('Helvetica', 12, 'bold'))        
        self.text_widget.tag_config('from_me', foreground = 'black', background = 'yellow', font=('Helvetica', 12, 'bold'))
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
        rx_message = e.widget.get(f"{curr}.0", f"{curr}.end")
        reply = determine_reply(rx_message, '-5')
        self.tx.set_transmit_payload(reply)

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
        idx = 1 * ("==" in text) + 2 * text.startswith("CQ") + 3* text.startswith(myCall) +4 * (text.split(' ')[1] == myCall)
        mtype = ['norm','info', 'cq','to_me','from_me'][idx]
        self.text_widget.insert(tk.END, text, mtype)
        self.text_widget.see('end')

app = App(tk.Tk())
app.root.mainloop()
