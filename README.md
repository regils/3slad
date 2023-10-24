# 3slad

3SLAD is a decoder which uses sigrok, it works with 2 channels and has 3 states: High, Medium and Low.
It also has X state which is prohibited state.

INSTALLATION

1. To install the decoder you need a signal analysis software which uses sigrok to be installed on your computer (e.g. PulseView, DSView).
2. Once first step is done, download a ZIP-archive with decoder.
3. Find the signal analysis software folder and go to folder with all decoders.
I'm using PulseView and in my case all decoders are located in:
C:\Program Files (x86)\sigrok\PulseView\share\libsigrokdecode\decoders
4. Once folder with decoders has been found successfully, unzip the archive into that folder and you're done.
Now you can finally use this decoder, just find it in your decoder list and add it.
