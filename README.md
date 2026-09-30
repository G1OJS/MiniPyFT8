# MiniPyFT8 
This repo contains a minimised FT8 decoder written entirely in Python, together with a minimal transmitter and GUI which can together comprise a simple transceiver. Please see the [README](https://github.com/G1OJS/PyFT8/blob/main/README.md) in  [PyFT8](https://github.com/G1OJS/PyFT8) for more information.

<img width="651" height="411" alt="Capture" src="https://github.com/user-attachments/assets/758154dd-8703-41e8-8064-e93f6db0813e" />

## Uses
This is really a 'toy' decoder/transceiver, but it illustrates what can be done in a very few lines of Python. Currently, the code comprises:
 - Receiver ~ 300 lines
 - Transmitter ~ 300 lines
 - Tkinter GUI ~ 100 lines

That's an FT8 transmitter / receiver in about 700 lines of Python, including LDPC decoding.

If you want to use it to transmit, please edit myCall and myGrid in tk_tcvr.py to reflect your own details! I'll come back soon and add entry boxes for these, and a CQ button ...

## Acknowledgements
This project implements a decoder for the FT8 digital mode. FT8 was developed by Joe Taylor, K1JT, Steve Franke, K9AN, and others as part of the WSJT-X project.
Protocol details are based on information publicly described by the WSJT-X authors and in related open documentation.

Some constants and tables (e.g. Costas synchronization sequence, LDPC structure, message packing scheme) are derived from 
the publicly available WSJT-X source code and FT8 protocol descriptions. Original WSJT-X source is © the WSJT Development Group 
and distributed under the GNU General Public License v3 (GPL-3.0), hence the use of GPL-3.0 in this repository.

