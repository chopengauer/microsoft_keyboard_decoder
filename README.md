Microsoft Keyboard decoder
Some kinda keysweeper

Tested on device:
045e:0745 Microsoft Corp. Nano Transceiver v1.0 for Bluetooth


# You can scan and decode it with nrf24 with Raspberry
decoder_on_raspberry.py
As input parameters you should give channel, address and keystream.


# You can scan and decode it with SDR. 
Configured for HackRF/ any osmosdr source.
decoder_on_sdr.py
For changes - open gnuradio model (GRC).
SDR -> GnuRadio(nrf.grc + nrf.py) -> pipe(fifo) -> nrf24_analyzer -> decoder_on_sdr.py
