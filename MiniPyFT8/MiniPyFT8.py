import tkinter as tk
import tkinter.scrolledtext as st
import time, threading, socket, queue
from MiniPyFT8.receiver import Receiver
from PyFT8.transmitter import get_ft8_symbols, symbols_to_audio_bytes
MAX_TX_START_CYCLETIME = 3

"""
class QSO_manager:
    def __init__(self, myCall, myGrid, rig_control, soundcard_out, console_print, waterfall_data):
        self.soundcard_out = soundcard_out
        self.waterfall_data = waterfall_data
        self.in_qso_with = False
        self.tx_payload, self.last_tx_payload = None, None
        self.band_info = {'current_band': None, 'fMHz':0}
        self.transmitting = False
        self.tx_cycle = 0
        self.console_print = console_print
        self.rig = rig_control
        self.myCall, self.myGrid = myCall, myGrid
        self.tx_freq = 750
        self.console_print(f"[PyFT8] QSO handler started for {self.myCall}")
        threading.Thread(target = self._transmit_daemon, daemon = True).start()

    def _find_clear_freq(self, fmax):
        import numpy as np
        fbin_sum = np.sum(self.waterfall_data['data'], axis = 1)
        f0_idx, fn_idx = int(500/self.waterfall_data['df']), int(fmax/self.waterfall_data['df'])
        idx = np.argmin(fbin_sum[f0_idx:fn_idx])
        clearest_frequency = (f0_idx + idx) * self.waterfall_data['df']
        return clearest_frequency

    def _start_qso(self, their_call, their_snr, tx_cycle, band_info):
        gmt = time.gmtime()
        self.logging_info = {'operator':self.myCall, 'station_callsign':self.myCall, 'my_gridsquare':self.myGrid, 'mode':'FT8',
                             'time_on': time.strftime("%H%M%S", gmt), 'qso_date':time.strftime("%Y%m%d", gmt),
                             'band':band_info['current_band'], 'freq':band_info['fMHz'],
                             'call':their_call, 'rst_sent':their_snr}
        self.tx_cycle = tx_cycle
        maxfreq = 950 if self.band_info['current_band'] == '60m' else 2500
        self.tx_freq = self._find_clear_freq(maxfreq)
        self.in_qso_with = their_call

    def _add_their_report_or_grid(self, grid_rpt):
        if any([m for m in ['+','-'] if m in grid_rpt]): # grid_rpt == rpt
            self.logging_info.update({'rst_rcvd': grid_rpt})
        if not any([m for m in ['+','-','RR','73'] if m in grid_rpt]): # grid_rpt == grid
            self.logging_info.update({'gridsquare': grid_rpt})

    def _determine_reply(self, message_type, their_call, their_snr, grid_rpt):
        if message_type == "CQ":
            reply = f"{their_call} {self.myCall} {self.myGrid[:4]}"   
        if message_type == "to_me":
            reply = f"{their_call} {self.myCall} {their_snr}"
            if any([m for m in ['+','-'] if m in grid_rpt]):
                reply = f"{their_call} {self.myCall} R{their_snr}"
            if any([m for m in ['R+','R-','RRR'] if m in grid_rpt]):
                reply = f"{their_call} {self.myCall} RR73"
            if grid_rpt == 'RR73':
                reply = f"{their_call} {self.myCall} 73"
        return reply

    def _end_qso(self):
        gmt = time.gmtime()
        print({'time_off': time.strftime("%H%M%S", gmt), 'qso_date_off':time.strftime("%Y%m%d", gmt)})
        self.in_qso_with = False

    def on_click(self, clickargs):
        btn_action = clickargs['action']
        if btn_action == "TX_OFF":
            self.console_print("[PyFT8] Set PTT Off")
            self.rig.ptt_off()
            self.tx_payload = None
        if self.transmitting:
            return
        if btn_action in ['MESSAGE_CLICK','CQ'] and self.band_info['current_band'] is None:
            self.console_print("Please select a band before transmitting", color = 'red')
            return
        if btn_action == "SET_BAND":
            self.band_info = clickargs['band_info']
            self.rig.set_freq_Hz(int(1000000*float(self.band_info['fMHz'])))
        if btn_action == "CQ":
            tnow = time.time()
            self.tx_cycle = int(tnow / T_CYC) % 2
            if tnow % T_CYC > MAX_TX_START_CYCLETIME:
                self.tx_cycle = 1 - self.tx_cycle 
            self._set_tx_payload(f"CQ {self.myCall} {self.myGrid[:4]}")
        if btn_action == "RPT_LAST":
            self.tx_payload = self.last_tx_payload

        if btn_action == "MESSAGE_CLICK":
            m = clickargs['message']
            short_msg = ' '.join(m['msg_tuple'])
            self.console_print(f"[QSO] Clicked on message '{short_msg}'")
            self._reply_to_message(m)


    def process_message(self, m):
        if self.in_qso_with == m['msg_tuple'][1]:
            if m['msg_tuple'][0] == self.myCall:
                short_msg = ' '.join(m['msg_tuple'])
                self.console_print(f"[QSO] Auto reply to message '{short_msg}'")
                self._reply_to_message(m)

    def _reply_to_message(self, m):
        message_type = m['message_type']
        if message_type in ['CQ','to_me'] and m['band'] == self.band_info['current_band']:
            _ , their_call, grid_rpt = m['msg_tuple']
            their_call = their_call.replace('<','').replace('>','')
            their_snr = m['their_snr']
            their_tx_cycle = m['their_tx_cycle']
            if their_call != self.in_qso_with:
                self._start_qso(their_call, their_snr, 1 - their_tx_cycle, self.band_info)
            self._add_their_report_or_grid(grid_rpt)
            reply = self._determine_reply(message_type, their_call, their_snr, grid_rpt)
            self._set_tx_payload(reply)
            if reply.endswith("73"):
                self._end_qso()

    def _set_tx_payload(self, tx_text):
        self.console_print(f"[QSO] Set transmit m to '{tx_text}' (cyc {self.tx_cycle}, {self.tx_freq:5.1f} Hz)")
        if len(tx_text.split(' ')) == 3:           
            symbols = get_ft8_symbols(tx_text)
            audio_bytes = symbols_to_audio_bytes(symbols, f_base = self.tx_freq)
            self.tx_payload = {'audio_bytes':audio_bytes, 'start_gridtime':[0.25, 15.25][self.tx_cycle]}
        else:
            self.console_print(f"[QSO] m is malformed", color = 'red')
            
    def _transmit_daemon(self):
        while True:
            time.sleep(0.1)
            if self.tx_payload is not None:
                start_gridtime = self.tx_payload['start_gridtime'] 
                grid_time = time.time() % (2 * T_CYC)
                if start_gridtime <= grid_time < start_gridtime + MAX_TX_START_CYCLETIME:
                    self.rig.ptt_on()
                    self.transmitting = True
                    self.soundcard_out.transmit_audio_data_bytes(self.tx_payload['audio_bytes'])
                    self.rig.ptt_off()
                    self.transmitting = False
                    self.last_tx_payload = self.tx_payload
                    self.tx_payload = None

"""

class App:
    def __init__(self, root):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 2121))
        self.rx = Receiver()
        self.decode_queue = queue.Queue()
        self.root = root
        self.frame = tk.Frame(self.root, bd = 2, bg = 'lightgrey')
        self.frame.pack(padx=1, pady=1, side='left', fill='both', expand=True)
        self.frm_decodes = tk.Frame(self.frame, bd = 2, bg = 'lightgrey', width = 600, height = 400)
        self.frm_decodes.pack(padx=1, pady=1, side='left', fill='both', expand=True)
        self.scrl_decodes = st.ScrolledText(self.frm_decodes)
        self.scrl_decodes.pack()
        self.root.bind("<<received_decode>>", self.received_decode)
        threading.Thread(target = self.monitor_socket, daemon = True).start()

    def monitor_socket(self):
        while True:
            time.sleep(0.1)
            decode_text, addres = self.sock.recvfrom(1024)
            decode_text = decode_text.decode()
            if decode_text:
                print(decode_text)
                self.decode_queue.put(f"{decode_text}\n")
                self.root.after(0, lambda: self.root.event_generate("<<received_decode>>"))

    def received_decode(self, e):
        text = self.decode_queue.get()
        self.scrl_decodes.insert(tk.INSERT, text)


        


app = App(tk.Tk())
app.root.mainloop()
