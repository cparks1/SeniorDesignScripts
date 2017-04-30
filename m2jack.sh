#!/bin/bash
# This shell script is used to setup a MIDI input device to output audio
# directly to the Raspberry PI's audio (3.5mm) jack.
# Engineer: Christopher Parks (cparks 13 AT live DOT com)

# Create directory "MIDI2jack" in "/usr/bin/".
# At the following line to the end of "~/.profile" (~ stands for your home dir):
# "/usr/bin/MIDI2jack/m2jack.sh"

fluidsynth -is --audio-driver=alsa --gain 6 /usr/share/sounds/sf2/FluidR3_GM.sf2 &
sleep 10
aconnect 20 128
