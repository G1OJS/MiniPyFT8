# MiniPyFT8 
This repo contains a minimised FT8 decoder written entirely in Python, using Matplotlib to display the waterfall.

It includes an annotated waterfall and LDPC decoder in about 300 lines of Python code. 

It is a derivative of my fuller decoder [PyFT8](https://github.com/G1OJS/PyFT8) which includes transmit capability but no waterfall. Please see the [README](https://github.com/G1OJS/PyFT8/blob/main/README.md) in that repo for more information.

<img width="1004" height="1042" alt="screenshot" src="https://github.com/user-attachments/assets/d92efaaa-659c-4ee3-8151-9d1874b8afce" />

## Uses
This is really a 'toy' decoder but it illustrates what can be done in about 300 lines of Python. To run it, download the main Python file and run it as main from your favourite IDE, or develop it as you wish. I might make it into a PyPi package with a CLI at some point. 

## Acknowledgements
This project implements a decoder for the FT8 digital mode. FT8 was developed by Joe Taylor, K1JT, Steve Franke, K9AN, and others as part of the WSJT-X project.
Protocol details are based on information publicly described by the WSJT-X authors and in related open documentation.

Some constants and tables (e.g. Costas synchronization sequence, LDPC structure, message packing scheme) are derived from 
the publicly available WSJT-X source code and FT8 protocol descriptions. Original WSJT-X source is © the WSJT Development Group 
and distributed under the GNU General Public License v3 (GPL-3.0), hence the use of GPL-3.0 in this repository.

