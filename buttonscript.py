#Engineer: Christopher Parks
#Contact: cparks13 at live dot com

# Add the following line to the end of "/etc/rc.local", before "exit 0":
# "python /home/pi/buttonscript.py &"

import RPi.GPIO as GPIO
import time
import subprocess

import os
import signal
import subprocess
import easygui  # Used for notifying user that usb storage not present


GPIO.setmode(GPIO.BCM) #Setup BCM GPIO numbering, which means GPIO pins will be referred to by name
GPIO.setup(8,GPIO.IN,pull_up_down=GPIO.PUD_DOWN) #Setup GPIO port 8 as an input
GPIO.setup(7,GPIO.OUT) # Setup GPIO port 7 as an output for an LED
GPIO.output(7,False) # Turn the LED on

globool = False #Used to determine whether we are beginning or ending recording
lastGPIOval = 0 #Used to determine whether the button press is rising or falling

global process# = None #Used to handle recording process
pid = 0 #Used to handle holding the PID of the recording process

global path # Used to store the location of the recorded mid file.

def but_rise(channel): # Catches the rising edge of a pin change on GPIO pin 8
        global globool
        global process
        global pid
        global path
        globool = not globool #Switches the variable we use to track recording state
        GPIO.output(7, globool) #Switches a recording indicator LED on/off
        if globool: # Begin recording
                dirss = os.walk("/media/pi")
                dirs = [x[0] for x in dirss]
                if len(dirs) > 1:
                        dir = dirs[1]
                        print dir
                        print "Beginning recording..."
                        path = dir+time.strftime("/%m-%d-%Y_%H-%M-%S")+'.mid'
                        process = subprocess.Popen(['smfrec','-d','20:0',path],shell=False)
                        pid = process.pid
                        print(str(pid) + "    " + str(process))
                else:
                        print("No external media detected.")
                        easygui.msgbox("No external storage detected. Insert external storage via USB and try again.", title="ERROR")
                        #subprocess.Popen(['espeak','-s125','"No external storage detected. Insert external storage via USB and  try again."'])
        else: #End recording
                if process is not None and pid !=0:
                        process.send_signal(signal.SIGINT) #Send CTRL-C to end recording
                        print(str(process))
                        print "Ending recording..."
                        if not process.poll():                                                                
                                print "Recording successfully ended."
                                print "Here is path:"+path
                                while not os.path.exists(path):
                                    time.sleep(1)
                                with open(path, 'r+') as old_buffer:
                                    new_buffer = old_buffer.read(61) # copy until 61th byte of file (after what we believe to be the setup of the midi file)
                                    new_buffer += '\x00\xC0\x0E' # insert new content (C0 is a MIDI program change. We're unsure what 0F 19 stands for, but 0E is the instrument number. (bells)
                                    new_buffer += old_buffer.read() # copy the rest of the file (Grab the rest of the midi file)
                                    old_buffer.seek(0,0)
                                    old_buffer.truncate() #Wipe the file
                                    old_buffer.write(new_buffer) # And save the new MIDI File with bell instrument change inserted

#def fall_but(channel): #Commented out. Not needed.
#        print "Falling edge detected"

GPIO.add_event_detect(8, GPIO.RISING, callback=but_rise, bouncetime=600) # Adds a pin change interrupt and connects it to the function "but_rise"

try:
        while True: # Keep the program running
                time.sleep(0.1) # Part of the while loop keeping the program running.
except KeyboardInterrupt:
        print "Closing recording button catch script...\n"
finally:
        GPIO.cleanup()
