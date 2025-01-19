# Sofabaton Control
Python service for the Sofabaton U2 to provide a remote control interface into linux.

* This was developed to provide an interface into the [FieldStation42](https://github.com/shane-mason/FieldStation42) project written by [shane-mason](https://github.com/shane-mason).
* Its only function is to let the Sofabaton U2 use its bluetooth pairing to send button press codes to the linux system and write them to the channel.socket that FieldStation42 monitors for channel change inputs.

## Dependencies:
* Tested with Linux 6.6.62+rpt-rpi-2712 #1 SMP PREEMPT Debian 1:6.6.62-1+rpt1 (2024-11-25) aarch64 GNU/Linux
* Tested to run on a Raspberry Pi 5
* evtest
* SofaBaton U2 needs to be paired with Linux


# Pairing SofaBaton U2 with Linux
To use SofaBaton Control, you will need to pair the SofaBaton U2 to the Raspberry Pi. 

I configured the SofaBaton U2 with my Android phone, using the SofaBaton app found on the Google Play store.

Upon launching the SofaBaton app, it should prompt to specify which series of SofaBaton you have.  Select the U Series, then follow the directions for pairing it to your phone (i.e., press the - and E keys).  Take note of the MAC address of your SofaBaton and press the connect button.  

*Note: I noticed that sometimes the SofaBaton app would appear to hang and not do anything.  To resolve this, I restarted the SofaBaton app and tried again, and then it would connect.

Next, use the Add button and follow the prompts to add a device type.  I chose 'Bluetooth Keyboard'.  Continue to follow the prompts and complete the pairing process.

On the Raspberry Pi OS, you can use the Bluetooth pairing UI to add the SofaBatonxxxxx device. During discovery, the Raspberry Pi OS detected my SofaBaton as SofaBaton05666.




# Discovering Bluetooth Button Press Codes
In this section, I'm providing directions on how to discover the key presses for a SofaBaton U2.  Technically this process should work with any bluetooth type of remote, but these directions only focus on the SofaBaton U2.

You will need the evtest package.

`sudo apt install evtest`

Launch the evtest utility:

`python3 /usr/lib/python3/dist-packages/evdev/evtest.py`

Several devices will likely be listed.  Below is an example of my SofaBaton to help you discover yours.  Your event numbers may be different and will require that you do some discovery.

```bash
8   /dev/input/event8    Sofabaton05666 Consumer Control     2c:cf:67:71:d6:23                   00:05:08:24:36:66

9   /dev/input/event9    Sofabaton05666 Keyboard             2c:cf:67:71:d6:23                   00:05:08:24:36:66
```

The following apply to the event8 and event9 above:

* The /dev/input/event8 is the Consumer Control aspects of the SofaBaton, and are linked with the /dev/input/event8, which provides a linkage to specialized keys like reverse, play, fast-forward, etc.
* The /dev/input/event9 (Sofabaton05666 Keyboard) is where the number keys are registered. In the sofabaton_control.py the design focuses exclusively on the number buttons and the E button.  


# Known Button Press Codes
The following is a list of known codes and their respective device mapping:

```bash116 	# Power; /dev/input/event8
130	# Menu (hamburger symbol); /dev/input/event9
71	# Home; /dev/input/event9
115	# Volume Up; /dev/input/event9
114	# Volume Down; /dev/input/event9
103	# Up Arrow; /dev/input/event9
108	# Down Arrow; /dev/input/event9
105	# Left Arrow;  /dev/input/event9
106	# Right Arrow; /dev/input/event9 
353	# OK button; /dev/input/event8
113	# Mute; /dev/input/event8
158	# Return; /dev/input/event8
168	# Reverse; /dev/input/event8
207	# Play; /dev/input/event8
208	# Fast Forward; /dev/input/event8
167	# Record; /dev/input/event8
164	# Pause; /dev/input/event8
166	# Stop; /dev/input/event8
2	# 1 Button; /dev/input/event9
3	# 2 Button; /dev/input/event9
4	# 3 Button; /dev/input/event9
5	# 4 Button; /dev/input/event9
6	# 5 Button; /dev/input/event9
7	# 6 Button; /dev/input/event9
8	# 7 Button; /dev/input/event9
9	# 8 Button; /dev/input/event9
10	# 9 Button; /dev/input/event9
11	# 0 Button; /dev/input/event9
18	# E Button; /dev/input/event9

* Note: The following buttons are currently unknown:
???	# Channel Up; ???
???	# Channel Down; ???
???	# Info (i symbol inside circle); ???
???	# - (found to the left of 0 button); ???
```

These codes that are needed for channel input have been integrated into sofabaton_control.py.



# Setup sofabaton_control.py to be a service
The sofabaton_control.py can be run as a standalone utility from the command line simply by entering:

`python3 sofabaton_control.py`

To integrate sofabaton_control.py into the OS to run you will need to tailor the sofabaton_control.py to fit your environment.  You will need to edit the following values in **sofabaton_control.py**:

**COMMAND_FILE**	# Point to the location of the file that you want to write key binds to, such as channel.lock on FieldStation42.

**REMOTE_DEVICE**	# See the section, "Discovering Bluetooth Button Press Codes" and supply the /dev/input/eventx number that is found on your system.

Set execution privileges on sofabaton_control.py:

`chmod +x sofabaton_control.py`

Next, place the sofabaton_control.service into /lib/systemd/system.

`sudo cp sofabaton_control.py /lib/systemd/system`

Then edit the sofabaton_control.service and edit the following values to match your environment:

**ExecStart**	# Point to the location where sofabaton_control.py is placed.

**User**		# This should match your userid.

**WorkingDirectory**	# This should match your environment.



Next, setup a symbolic link:

`sudo ln -s /lib/systemd/system/sofabaton_control.service /etc/systemd/system/sofabaton_control.service`

Then:

`sudo systemctl daemon-reload`

`sudo systemctl enable sofabaton_control.service`

`sudo systemctl start sofabaton_control.service`

Test:

`sudo systemctl status sofabaton_control.service`

* Note: The following illustrates a working configuration.  If your service if not starting, then doublecheck the REMOTE_DEVICE entry and make sure you're pointing to the correct /dev/input/eventx device.

```bash
jtburkh@blackacreTV:/etc/systemd/system $ sudo systemctl status sofabaton_control.service
● sofabaton_control.service - Sofabaton Remote Control for FieldStation42
     Loaded: loaded (/lib/systemd/system/sofabaton_control.service; bad; preset: enabled)
     Active: active (running) since Sun 2025-01-19 12:52:47 PST; 1min 31s ago
   Main PID: 3940 (python3)
      Tasks: 1 (limit: 9559)
        CPU: 108ms
     CGroup: /system.slice/sofabaton_control.service
             └─3940 /usr/bin/python3 /home/jtburkh/sofabaton_control.py

Jan 19 12:52:47 blackacreTV systemd[1]: Started sofabaton_control.service - Sofabaton Remote Control for FieldStation42.
```



# How to Use

This utility is made to integrate with the FieldStation42 project.  It assumes that you have a FieldStation42 running and that there are more than one channels running.  It will technically still work if you don't have more than one channel, but is intended to help you change channels.

`Press one or more numbers on your Sofabaton U2 and then press 'E'. `

* This will send the button press numbers to the linux system and when the E key is pressed, the sofabaton_control will dump the buffer into a properly formatted JSON snippet then place it into the channel.socket file. FieldStation42 takes it from there and changes the channel to whatever you inputted.

