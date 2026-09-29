import serial, time, socket, subprocess, threading, psutil

class Rig_CAT:
    def __init__(self, config, verbose = False, port = 'COM4', baud_rate = 9600,
                 ptt_on_cmd = 'FEFE88E0.1C00.01.FD', ptt_off_cmd = 'FEFE88E0.1C00.00.FD',
                 set_freq_cmd = 'FEFE88E0.05.0000000000.FD',
                 set_freq_value = '5|5|vfBcdLU|1|0'):
        self.serial_port = False
        self.port, self.baud_rate = port, baud_rate
        self.ptt_on_cmd, self.ptt_off_cmd = ptt_on_cmd, ptt_off_cmd
        self.set_freq_cmd, self.set_freq_value = set_freq_cmd, set_freq_value
        self.verbose = verbose

    def parse_configstr(self, configstr):
        if "." in configstr:
            hexstr = configstr.replace(".", "")
            return bytearray.fromhex(hexstr)
        else:
            return bytearray(configstr.encode())
        
    def vprint(self, text):
        if self.verbose:
            print(text)

    def _sendCAT(self, msg):
        try:
            self.serial_port = serial.Serial(port = self.port, baudrate = self.baud_rate, timeout = 0.1)
        except Exception as e:
            print(f"[CAT] couldn't open {self.port}: {e}")
        if (self.serial_port):
            self.serial_port.reset_input_buffer()
            self.vprint(f"[CAT] send {msg.hex(' ')}")
            try:
                self.serial_port.write(msg)
                time.sleep(0.05)
                self.serial_port.close()
            except Exception as e:
                print(f"[CAT] couldn't send CAT command {msg} on {self.port}: {e}")

    def set_freq_Hz(self, freqHz):
        if self.set_freq_cmd and self.set_freq_value:
            self.vprint(f"[CAT] SET frequency to {freqHz} Hz")
            start, length, fmt, mult, offset = self.set_freq_value.split("|")
            start, length, mult, offset = int(start), int(length), int(mult), int(offset)
            fVal = freqHz * mult + offset
            nDigits = length if fmt == "text" else 2*length
            s = f"{fVal:0{nDigits}d}"
            if fmt=='text':
                fBytes = s.encode()
            else:
                pairs = [(int(s[i]) << 4) | int(s[i+1]) for i in range(0, len(s), 2)]
                if fmt == "vfBcdLU":
                    fBytes = bytes(pairs[::-1])
                else:
                    fBytes = bytes(pairs)
            cmd = bytearray(self.set_freq_cmd)
            cmd[start:start+length] = fBytes
            if fmt.startswith("vfBcd"):  # CI-V
                cmd = b'\x00' + cmd
            self._sendCAT(cmd)

    def ptt_on(self):
        if self.ptt_on_cmd:
            self.vprint(f"[CAT] PTT On")
            self._sendCAT(self.ptt_on_cmd)

    def ptt_off(self):
        if self.ptt_off_cmd:
            self.vprint(f"[CAT] PTT Off")
            self._sendCAT(self.ptt_off_cmd)

class Rig_hamlib:
    def __init__(self, com = 'COM4', s = 9600, rigctld = 'C:/WSJT/wsjtx/bin/rigctld-wsjtx', rig = 3070, host = 'localhost', port = 4532):
        if not any(['rigctld' in i.name() for i in psutil.process_iter()]):
            cmd = f"{rigctld} -m {rig} -r {com} -s {s}"
            threading.Thread(target = subprocess.run, args = (cmd,)).start()
            time.sleep(0.5)
        self.sock = socket.create_connection((host, port))
        self.set_mode("PKTUSB")

    def cmd(self, command):
        if self.sock:
            self.sock.sendall((command + "\n").encode())
            return self.sock.recv(1024).decode()

    def set_mode(self, mode):
        self.cmd(f"M {mode} 0")

    def set_freq_Hz(self, hz):
        self.cmd(f"F {hz}")

    def ptt_on(self):
        self.cmd(f"T 1")

    def ptt_off(self):
        self.cmd(f"T 0")


