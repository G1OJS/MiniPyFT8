import tkinter as tk
from tkinter import ttk
import time, threading, socket, queue, json
from receiver import Receiver
from transmitter import Transmitter

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
        self.sock_tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
        self.current_decodes = []
        self.root.bind("<<received_udp>>", self.received_udp)
        threading.Thread(target = self.monitor_udp, daemon = True).start()
        
    def send_udp(self, msg):
        self.sock_tx.connect(('localhost', 2122))
        self.sock_tx.send(json.dumps(msg).encode('utf-8'))

    def monitor_udp(self):
        while True:
            time.sleep(0.1)
            rx_bytes, addres = self.sock.recvfrom(1024)
            if rx_bytes:
                self.decode_queue.put(json.loads(rx_bytes.decode('utf-8')))
                self.root.after(0, lambda: self.root.event_generate("<<received_udp>>"))

    def received_udp(self, e):
        msg_dict = self.decode_queue.get()
        if msg_dict['mtype'] == 'decode':
            self.current_decodes.append(msg_dict)
            their_snr, fHz, dt, msg_tuple = msg_dict['their_snr'], msg_dict['fHz'], msg_dict['dt'], msg_dict['msg_tuple'], 
            idx = 1 * msg_tuple[0].startswith("CQ") + 2* msg_tuple[0].startswith(myCall) + 3 * (msg_tuple[1] == myCall)
            display_type = ['norm','cq','to_me','from_me'][idx]
            display_text = f"{their_snr:4s} {dt:5s} {fHz:6s} ~ {' '.join(msg_tuple)}"
        elif msg_dict['mtype'] == 'rollover':
            display_type = 'info'
            display_text = msg_dict['info']
        else:
            display_type = 'info'
            display_text = msg_dict['info']        
        self.text_widget.insert(tk.END, f"{display_text}\n", display_type)
        self.text_widget.see('end')

    def row_click(self, e):
        curr = e.widget.index("current").split('.')[0]
        row_txt = e.widget.get(f"{curr}.0", f"{curr}.end")
        if "~" in row_txt:
            rx_message = row_txt.split('~')[1][1:]
            their_snr = row_txt[:3]
            reply = determine_reply(rx_message, their_snr)
            self.send_udp({'mtype':'transmit', 'message':reply})



#rx = Receiver()
#tx = Transmitter()
app = App(tk.Tk())
app.root.mainloop()
