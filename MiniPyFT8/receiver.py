import numpy as np
import time, pyaudio, threading, queue, socket, json

params = {'HPS': 4, 'BPT':2,'SYM_RATE': 6.25,'SAMP_RATE': 12000,
          'T_SEARCH_0': 4.6, 'T_SEARCH_1': 10.6, 'PAYLOAD_SYMBOLS': 79-7, 'LDPC_CONTROL': (35, 12) }
params.update({'H0_RANGE': [0, int(3.6 * params['SYM_RATE'] * params['HPS'])]})

call_hashes = {}
def add_call_hash(call):
    global call_hashes
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
        call_hashes[(x,m)] = call

#=========== Unpacking functions ========================================
CALLSIGN_PREFIXES1 = "A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,R,S,T,U,V,W,X,Y,Z"
CALLSIGN_PREFIXES2 = "2A,2B,2C,2D,2E,2F,2G,2H,2I,2J,2K,2L,2M,2N,2O,2P,2Q,2R,2S,2T,2U,2V,2W,2X,2Y,2Z,3A,3B,3C,3D,3D,3E,3F,3G,3H,3I,3J,3K,3L,3M,3N,3O,3P,3Q,3R,3S,3T,3U,3V,3W,3X,3Y,3Z,4A,4B,4C,4D,4E,4F,4G,4H,4I,4J,4K,4L,4M,4O,4P,4Q,4R,4S,4T,4U,4V,4W,4X,4Y,4Z,5A,5B,5C,5D,5E,5F,5G,5H,5I,5J,5K,5L,5M,5N,5O,5P,5Q,5R,5S,5T,5U,5V,5W,5X,5Y,5Z,6A,6B,6C,6D,6E,6F,6G,6H,6I,6J,6K,6L,6M,6N,6O,6P,6Q,6R,6S,6T,6U,6V,6W,6X,6Y,6Z,7A,7B,7C,7D,7E,7F,7G,7H,7I,7J,7K,7L,7M,7N,7O,7P,7Q,7R,7S,7T,7U,7V,7W,7X,7Y,7Z,8A,8B,8C,8D,8E,8F,8G,8H,8I,8J,8K,8L,8M,8N,8O,8P,8Q,8R,8S,8T,8U,8V,8W,8X,8Y,8Z,9A,9B,9C,9D,9E,9F,9G,9H,9I,9J,9K,9L,9M,9N,9O,9P,9Q,9R,9S,9T,9U,9V,9W,9X,9Y,9Z,A2,A3,A4,A5,A6,A7,A8,A9,AA,AB,AC,AD,AE,AF,AG,AH,AI,AJ,AK,AL,AM,AN,AO,AP,AQ,AR,AS,AT,AU,AV,AW,AX,AY,AZ,BA,BB,BC,BD,BE,BF,BG,BH,BI,BJ,BK,BL,BM,BN,BO,BP,BQ,BR,BS,BT,BU,BV,BW,BX,BY,BZ,C2,C3,C4,C5,C6,C7,C8,C9,CA,CB,CC,CD,CE,CF,CG,CH,CI,CJ,CK,CL,CM,CN,CO,CP,CQ,CR,CS,CT,CU,CV,CW,CX,CY,CZ,D2,D3,D4,D5,D6,D7,D8,D9,DA,DB,DC,DD,DE,DF,DG,DH,DI,DJ,DK,DL,DM,DN,DO,DP,DQ,DR,DS,DT,DU,DV,DW,DX,DY,DZ,E2,E3,E4,E5,E6,E7,EA,EB,EC,ED,EE,EF,EG,EH,EI,EJ,EK,EL,EM,EN,EO,EP,EQ,ER,ES,ET,EU,EV,EW,EX,EY,EZ,FA,FB,FC,FD,FE,FF,FG,FH,FI,FJ,FK,FL,FM,FN,FO,FP,FQ,FR,FS,FT,FU,FV,FW,FX,FY,FZ,GA,GB,GC,GD,GE,GF,GG,GH,GI,GJ,GK,GL,GM,GN,GO,GP,GQ,GR,GS,GT,GU,GV,GW,GX,GY,GZ,H2,H3,H4,H6,H7,H8,H9,HA,HB,HC,HD,HE,HF,HG,HH,HI,HJ,HK,HL,HM,HN,HO,HP,HQ,HR,HS,HT,HU,HV,HW,HX,HY,HZ,IA,IB,IC,ID,IE,IF,IG,IH,II,IJ,IK,IL,IM,IN,IO,IP,IQ,IR,IS,IT,IU,IV,IW,IX,IY,IZ,J2,J3,J4,J5,J6,J7,J8,JA,JB,JC,JD,JE,JF,JG,JH,JI,JJ,JK,JL,JM,JN,JO,JP,JQ,JR,JS,JT,JU,JV,JW,JX,JY,JZ,KA,KB,KC,KD,KE,KF,KG,KH,KI,KJ,KK,KL,KM,KN,KO,KP,KQ,KR,KS,KT,KU,KV,KW,KX,KY,KZ,L2,L3,L4,L5,L6,L7,L8,L9,LA,LB,LC,LD,LE,LF,LG,LH,LI,LJ,LK,LL,LM,LN,LO,LP,LQ,LR,LS,LT,LU,LV,LW,LX,LY,LZ,MA,MB,MC,MD,ME,MF,MG,MH,MI,MJ,MK,ML,MM,MN,MO,MP,MQ,MR,MS,MT,MU,MV,MW,MX,MY,MZ,NA,NB,NC,ND,NE,NF,NG,NH,NI,NJ,NK,NL,NM,NN,NO,NP,NQ,NR,NS,NT,NU,NV,NW,NX,NY,NZ,OA,OB,OC,OD,OE,OF,OG,OH,OI,OJ,OK,OL,OM,ON,OO,OP,OQ,OR,OS,OT,OU,OV,OW,OX,OY,OZ,P2,P3,P4,P5,P6,P7,P8,P9,PA,PB,PC,PD,PE,PF,PG,PH,PI,PJ,PJ,PJ,PK,PL,PM,PN,PO,PP,PQ,PR,PS,PT,PU,PV,PW,PX,PY,PZ,RA,RB,RC,RD,RE,RF,RG,RH,RI,RJ,RK,RL,RM,RN,RO,RP,RQ,RR,RS,RT,RU,RV,RW,RX,RY,RZ,S2,S3,S5,S6,S7,S8,S9,SA,SB,SC,SD,SE,SF,SG,SH,SI,SJ,SK,SL,SM,SN,SO,SP,SQ,SR,SS,SS,ST,SU,SV,SW,SX,SY,SZ,T2,T3,T4,T5,T6,T7,T8,TA,TB,TC,TD,TE,TF,TG,TH,TI,TJ,TK,TL,TM,TN,TO,TP,TQ,TR,TS,TT,TU,TV,TW,TX,TY,TZ,UA,UB,UC,UD,UE,UF,UG,UH,UI,UJ,UK,UL,UM,UN,UO,UP,UQ,UR,US,UT,UU,UV,UW,UX,UY,UZ,V2,V3,V4,V5,V6,V7,V8,VA,VB,VC,VD,VE,VF,VG,VH,VI,VJ,VK,VL,VM,VN,VO,VP,VQ,VR,VS,VT,VU,VV,VW,VX,VY,VZ,WA,WB,WC,WD,WE,WF,WG,WH,WI,WJ,WK,WL,WM,WN,WO,WP,WQ,WR,WS,WT,WU,WV,WW,WX,WY,WZ,XA,XB,XC,XD,XE,XF,XG,XH,XI,XJ,XK,XL,XM,XN,XO,XP,XQ,XR,XS,XT,XU,XV,XW,XX,XY,XZ,Y2,Y3,Y4,Y5,Y6,Y7,Y8,Y9,YA,YB,YC,YD,YE,YF,YG,YH,YI,YJ,YK,YL,YM,YN,YO,YP,YQ,YR,YS,YT,YU,YV,YW,YX,YY,Z2,Z3,Z8,ZA,ZB,ZC,ZD,ZE,ZF,ZG,ZH,ZI,ZJ,ZK,ZL,ZM,ZN,ZO,ZP,ZQ,ZR,ZS,ZT,ZU,ZV,ZW,ZX,ZY,ZZ"

def get_bitfields(bits, lengths):
    fields = []
    for n in lengths:
        mask = (1 << n) - 1
        fields.append(bits & mask)
        bits >>= n
    return *fields, bits

def unpack(bits):
    if not bits:
        return None
    
    i3, bits74 = get_bitfields(bits,[3])
    if i3 == 0:
        n3, bits71 = get_bitfields(bits74,[3])
        if n3 <= 4:
            #return (['Free text', 'DXpedition', 'Field Day', 'Field Day', 'Telemetry'][n3], 'not', 'implemented')
            return None
        else:
            #return ('Unknown mode','not','implemented')
            return None
    elif i3 == 1 or i3 == 2: # 1 = Std Msg incl /R 2 = 'EU VHF' = Std Msg incl /P
        return unpack_std(bits74, i3)
    elif i3 == 3:
        #return ('RTTY RU','not','implemented')
        return None
    elif i3 == 4:
        cq, rrr, swp, c58, hsh, _ = get_bitfields(bits74, [1,2,1,58,12])
        if cq and rrr or (not cq and not rrr):
            return None
        ca = "CQ" if cq else f"<{call_hashes.get((hsh,12), '...')}>"
        cb = ""
        for i in range(12):
            cb = " 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ/"[c58 % 38] + cb
            c58 = c58 // 38
        cb =  cb.strip()
        add_call_hash(cb)
        (ca, cb) = (cb, ca) if swp else (ca, cb)
        return (ca, cb, ('', 'RRR', 'RR73', '73')[rrr])
    elif i3 == 5:
        #return ('EU VHF','not','implemented')
        return None

def unpack_std(bits74, i3):
    g16, cb29, ca29, _ = get_bitfields(bits74,[16,29,29])
    g15 = g16 & 0x7FFF
    if g15 == 0:
        return None
    if g15 < 32400:
        a, nn = divmod(g15, 1800)
        b, nn = divmod(nn, 100)
        c, d = divmod(nn, 10)
        grid_rpt =  chr(65+a) + chr(65+b) + str(c) + str(d)
    elif g15 - 32400 <= 4:
        grid_rpt =  ('', '', 'RRR', 'RR73', '73')[g15 - 32400]
    else:
        prefix = 'R' if (g16 >> 15) else ''
        grid_rpt = prefix + f"{(g15 - 32435):+03d}"
    msg_tuple = (call_29(ca29, i3), call_29(cb29, i3), grid_rpt)
    if not ('' in msg_tuple) and not (None in msg_tuple):
        return msg_tuple

def call_29(call_int29, i3):    
    portable_rover = call_int29 & 1
    call_int28 = call_int29>>1
    if call_int28 < 3:
        return ['DE', 'QRZ', 'CQ'][call_int28]
    elif call_int28 < 1004:
        return f"CQ {call_int28 - 3:03d}"
    elif call_int28 < 21443:
        x, txt = call_int28 - 1003, ''
        for i in range(4):
            txt = " ABCDEFGHIJKLMNOPQRSTUVWXYZ"[int(x % 27)] + txt
            x //= 27
        return f"CQ {txt.strip()}"
    elif call_int28 < 2063592+4194303:
        return f"<{call_hashes.get((call_int28 - 2063592, 22), '...')}>"
    else:
        call = standard_call28(call_int28, i3)
        if call is not None:
            if portable_rover:
                call = call + ('/P' if i3 == 2 else '/R')
            if call.endswith("/R") and not call[0] in ['A','K','N','W']:
                return None
            add_call_hash(call)
            return call

def standard_call28(call_int28, i3):
    nn = call_int28 - (2063592 + 4194304)
    from string import ascii_uppercase as ltrs, digits as digs
    call_fields = [ (' ' + digs + ltrs, 36*10*27**3),   (digs + ltrs, 10*27**3), (digs + ' ' * 17, 27**3),
                    (' ' + ltrs, 27**2),           (' ' + ltrs,   27), (' ' + ltrs,   1) ]
    chars = []
    for alphabet, div in call_fields:
        idx, nn = divmod(nn, div)
        chars.append(alphabet[idx])
    call = ''.join(chars).strip()
    return simple_validate_call(call)

def simple_validate_call(call):
    if not ' ' in call and len(call)>=3:
        if call[0] in CALLSIGN_PREFIXES1 and call[1].isnumeric():
            if not (call[0] in "B,F,G,I,K,M,N,R,W" and call[2].isnumeric()):
                return call
        if call[:2] in CALLSIGN_PREFIXES2 and call[2].isnumeric():
            return call
        
def crc_unpack91(codeword91):
    bits91_int = 0
    for bit in (codeword91 > 0).astype(int).tolist():
        bits91_int = (bits91_int << 1) | bit
    bits77_int = bits91_int >> 14
    msg = None
    if(bits77_int > 0):
        crc14_int = 0
        for i in range(96):
            inbit = ((bits77_int >> (76 - i)) & 1) if i < 77 else 0
            bit14 = (crc14_int >> (14 - 1)) & 1
            crc14_int = ((crc14_int << 1) & ((1 << 14) - 1)) | inbit
            if bit14:
                crc14_int ^= 0x2757
        if crc14_int == bits91_int & 0b11111111111111:
            msg = unpack(bits77_int) 
    return msg, bits77_int

#============== LDPC Decoder ========================================================
CV6idx = np.array([[4,31,59,92,114,145],[5,23,60,93,121,150],[6,32,61,94,95,142],[5,31,63,96,125,137],[8,34,65,98,138,145],[9,35,66,99,106,125],[11,37,67,101,104,154],[12,38,68,102,148,161],[14,41,58,105,122,158],[0,32,71,105,106,156],[15,42,72,107,140,159],[10,43,74,109,120,165],[7,45,70,111,118,165],[18,37,76,103,115,162],[19,46,69,91,137,164],[1,47,73,112,127,159],[21,46,57,117,126,163],[15,38,61,111,133,157],[22,42,78,119,130,144],[19,35,62,93,135,160],[13,30,78,97,131,163],[2,43,79,123,126,168],[18,45,80,116,134,166],[11,49,60,117,118,143],[12,50,63,113,117,156],[23,51,75,128,147,148],[20,53,76,99,139,170],[34,81,132,141,170,173],[13,29,82,112,124,169],[3,28,67,119,133,172],[51,83,109,114,144,167],[6,49,80,98,131,172],[22,54,66,94,171,173],[25,40,76,108,140,147],[26,39,55,123,124,125],[17,48,54,123,140,166],[5,32,84,107,115,155],[8,53,62,130,146,154],[21,52,67,108,120,173],[2,12,47,77,94,122],[30,68,132,149,154,168],[4,38,74,101,135,166],[1,53,85,100,134,163],[14,55,86,107,118,170],[22,33,70,93,126,152],[10,48,87,91,141,156],[28,33,86,96,146,161],[21,56,84,92,139,158],[27,31,71,102,131,165],[0,25,44,79,127,146],[16,26,88,102,115,152],[50,56,97,162,164,171],[20,36,72,137,151,168],[15,46,75,129,136,153],[2,23,29,71,103,138],[8,39,89,105,133,150],[17,41,78,143,145,151],[24,37,64,98,121,159],[16,41,74,128,169,171]], dtype = np.int16)
CV7idx = np.array([[3,30,58,90,91,95,152],[7,24,62,82,92,95,147],[4,33,64,77,97,106,153],[10,36,66,86,100,138,157],[7,39,69,81,103,113,144],[13,40,70,87,101,122,155],[16,36,73,80,108,130,153],[44,54,63,110,129,160,172],[17,35,75,88,112,113,142],[20,44,77,82,116,120,150],[18,34,58,72,109,124,160],[6,48,57,89,99,104,167],[24,52,68,89,100,129,155],[19,45,64,79,119,139,169],[0,3,51,56,85,135,151],[25,50,55,90,121,136,167],[1,26,40,60,61,114,132],[27,47,69,84,104,128,157],[11,42,65,88,96,134,158],[9,43,81,90,110,143,148],[29,49,59,85,136,141,161],[9,52,65,83,111,127,164],[27,28,83,87,116,142,149],[14,57,59,73,110,149,162]], dtype = np.int16)

def calc_ncheck(llr):
    bits6 = llr[CV6idx] > 0
    parity6 = np.sum(bits6, axis=1) & 1
    bits7 = llr[CV7idx] > 0
    parity7 = np.sum(bits7, axis=1) & 1
    return int(np.sum(parity7) + np.sum(parity6))

def pass_messages(llr, CVidx, mC2V_prev, update_collector):
    if mC2V_prev is None:
        mC2V_prev = np.zeros(CVidx.shape, dtype=np.float32)
    mV2C = llr[CVidx] - mC2V_prev
    tanh_mV2C = np.tanh(-mV2C)
    tanh_mC2V = np.prod(tanh_mV2C, axis=1, keepdims=True)
    tanh_mC2V = tanh_mC2V / (tanh_mV2C + 0.001)
    alpha_atanh_approx = 1.18
    mC2V_curr  = tanh_mC2V / ((tanh_mC2V - alpha_atanh_approx) * (alpha_atanh_approx + tanh_mC2V))
    np.add.at(update_collector, CVidx, mC2V_curr - mC2V_prev)
    return mC2V_curr

def decode(p):
    llra = np.max(p[:, [4,5,6,7]], axis=1) - np.max(p[:, [0,1,2,3]], axis=1)
    llrb = np.max(p[:, [2,3,4,7]], axis=1) - np.max(p[:, [0,1,5,6]], axis=1)
    llrc = np.max(p[:, [1,2,6,7]], axis=1) - np.max(p[:, [0,3,4,5]], axis=1)
    llr = np.column_stack((llra, llrb, llrc))
    llr = llr.ravel()
    ncheck = calc_ncheck(llr)
    ldpc_it = 0
    if 0 < ncheck <= params['LDPC_CONTROL'][0]:
        llr = 3.5 * llr / (np.std(llr) + 0.01)
        llr = np.clip(llr, -3.7, 3.7)
        mC2V_prev6, mC2V_prev7 = None, None
        for ldpc_it in range(params['LDPC_CONTROL'][1]):
            update_collector = np.zeros_like(llr)
            mC2V_prev6 = pass_messages(llr, CV6idx, mC2V_prev6, update_collector)
            mC2V_prev7 = pass_messages(llr, CV7idx, mC2V_prev7, update_collector)
            llr += update_collector
            ncheck = calc_ncheck(llr)
            if(ncheck == 0):
                break                    
    if ncheck == 0:
        msg_tuple, bits77_int = crc_unpack91(llr[:91])
        return msg_tuple

#============== AUDIO ========================================================
class AudioIn:
    def __init__(self, input_device_keywords, max_freq):
        self.fft_len = int(params['BPT'] * params['SAMP_RATE'] // params['SYM_RATE'])
        fft_out_len = self.fft_len // 2 + 1
        self.nFreqs = int(fft_out_len * 2 * max_freq / params['SAMP_RATE'])
        self.audio_buffer = np.zeros(self.fft_len, dtype=np.float32)
        self.fft_in = np.zeros(self.fft_len, dtype=np.float32)
        self.fft_window = fft_window=np.hanning(self.fft_len).astype(np.float32)
        self.hops_per_cycle = int(15 * params['SYM_RATE'] * params['HPS'])
        self.grid_main = np.ones((self.hops_per_cycle, self.nFreqs), dtype = np.float32)
        indev = self.find_device(input_device_keywords)
        self.stream = pyaudio.PyAudio().open(
            format = pyaudio.paInt16, channels=1, rate = params['SAMP_RATE'], input = True, input_device_index = indev,
            frames_per_buffer = int(params['SAMP_RATE'] / (params['SYM_RATE'] * params['HPS'])), stream_callback=self._callback,)
        self.set_pointer()
        self.stream.start_stream()

    def find_device(self, device_str_contains):
        if isinstance(device_str_contains, str):
            device_str_contains = device_str_contains.split(',')
        pya = pyaudio.PyAudio()
        for dev_idx in range(pya.get_device_count()):
            name = pya.get_device_info_by_index(dev_idx)['name']
            match = True
            for pattern in device_str_contains:
                if (not pattern in name): match = False
            if(match):
                return dev_idx
        print(f"[Audio] No audio device found matching {device_str_contains}")

    def set_pointer(self):
        self.grid_main_ptr = int((time.time() % 15) * params['SYM_RATE']*params['HPS'])

    def _callback(self, in_data, frame_count, time_info, status_flags):
        samples = np.frombuffer(in_data, dtype=np.int16).astype(np.float32)
        ns = len(samples)
        self.audio_buffer[:-ns] = self.audio_buffer[ns:]
        self.audio_buffer[-ns:] = samples
        np.multiply(self.audio_buffer, self.fft_window, out=self.fft_in)
        z = np.fft.rfft(self.fft_in)[:self.nFreqs]
        self.grid_main[self.grid_main_ptr, :] = z.real*z.real + z.imag*z.imag
        self.grid_main_ptr = (self.grid_main_ptr + 1) % self.hops_per_cycle
        return (None, pyaudio.paContinue)

class Receiver:
    def __init__(self, mic_keywords = ['Mic', 'CODEC'], max_freq = 3100, output = 'udp'):
        self.audio_in = AudioIn(mic_keywords, max_freq)
        self.output = output
        self.decode_queue = queue.Queue()
        self.duplicate_filter = []
        self.sock_out = None
        threading.Thread(target = self.decode_manager, daemon=True ).start()
        threading.Thread(target = self.cycle_manager, daemon=True ).start()

    def send_output(self, msg_dict):
        if self.output == 'print':
            print(msg_dict)
            return
        if self.sock_out is None:
            self.sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_out.connect(('localhost', 2121))
        self.sock_out.send(json.dumps(msg_dict).encode('utf-8'))

    def decode_manager(self):
        while True:
            time.sleep(0.01)
            if not self.decode_queue.empty():
                sync, p = self.decode_queue.get()
                msg_tuple = decode(p)
                if msg_tuple and not msg_tuple in self.duplicate_filter:
                    their_snr = np.clip(int((np.max(p) - np.min(p))/2) - 58, -24, 24)
                    self.duplicate_filter.append(msg_tuple)
                    self.send_output({'mtype':'decode', 'cyclestart_string': sync['cs'],
                                      'fHz':f"{sync['fHz']:7.2f}", 'dt':f"{sync['dt']:+04.2f}",
                                      'their_snr':f"{their_snr:+03d}", 'msg_tuple':msg_tuple})
        
    def cycle_manager(self):
        nFreqs = self.audio_in.nFreqs
        dt = 1.0 / (params['SYM_RATE'] * params['HPS']) 
        payload_symb_idxs = list(range(7, 36)) + list(range(43, 72))
        base_payload_hops = np.array([params['HPS'] * s for s in payload_symb_idxs])
        hop_idxs_Costas =  np.arange(7) * params['HPS']
        base_freq_idxs = np.array([params['BPT'] // 2 + params['BPT'] * t for t in range(8)])
        syncs = {}
        csync = np.full((7, 8*params['BPT']), -1/7, np.float32)
        for sym_idx, tone in enumerate([3,1,4,0,6,5,2]):
            fbins = range(tone* params['BPT'], (tone+1) * params['BPT'])
            csync[sym_idx, fbins] = 1.0
            csync[sym_idx, 7 * params['BPT']:] = 0.0
        csync_flat =  csync.ravel()
        self.send_output({'mtype':'info', 'info':'Receiver starting'})
        
        while time.time() % 15 > 0.5:
            time.sleep(0.1)

        while True:
            t0_cyc = 15 * int(time.time() / 15)
            self.audio_in.set_pointer()
            time.sleep(params['T_SEARCH_1'])
            cycle_start_str = time.strftime("%y%m%d_%H%M%S", time.gmtime(t0_cyc))
            info = f"{cycle_start_str} ========================================"
            self.send_output({'mtype':'rollover', 'info':info})
            for f0_idx in range(int(100 / 3.125), nFreqs - 8 * params['BPT'], 1):
                time.sleep(0)
                freq_idxs = f0_idx + base_freq_idxs
                p = self.audio_in.grid_main[:, f0_idx:f0_idx+8*params['BPT']]
                p = 20*np.log10(p)
                syncs[f0_idx] = {'score':0, 'h0_idx':0, 'dt': 0}
                for h0_idx in range(params['H0_RANGE'][0], params['H0_RANGE'][1]):
                    hn_idx = h0_idx + base_payload_hops[-1]
                    sync_score = float(np.dot(p[h0_idx + hop_idxs_Costas + 36 * params['HPS'], :].ravel(), csync_flat))
                    test_sync = {'cs':cycle_start_str, 'score':sync_score, 'h0_idx':h0_idx, 'hn_idx': hn_idx, 'fHz': 3.125 * f0_idx, 'dt': h0_idx * dt - 0.7}
                    if test_sync['score'] > syncs[f0_idx]['score']:
                        syncs[f0_idx] = test_sync

            while not self.decode_queue.empty():
                self.decode_queue.get()
            t = time.time() % 15
            self.duplicate_filter = []
            print(f"{t:7.2f} start decode")
            while time.time() % 15 > t:
                time.sleep(0.1)
                hop_ptr = self.audio_in.grid_main_ptr
                f0_idxs = [f for f in list(syncs.keys()) if syncs[f]['score'] > 100
                           and (hop_ptr > syncs[f]['hn_idx'] or hop_ptr < syncs[f]['h0_idx'])]
                for f0_idx in f0_idxs:
                    hops, freq_idxs = syncs[f0_idx]['h0_idx'] + base_payload_hops, f0_idx + base_freq_idxs
                    p = self.audio_in.grid_main[np.ix_(hops, freq_idxs)]
                    p = 20*np.log10(p)
                    self.decode_queue.put((syncs[f0_idx].copy(), p))
                    syncs[f0_idx]['score'] = -1

        
if __name__ == "__main__":
    rx = Receiver(mic_keywords = ['Mic', 'CODEC'], max_freq = 2900, output = 'print')
 

