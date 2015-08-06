#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Projekt: Testbox Knauf IPA
# Datei: testboxkanuf.py
# Datum: 21.04.2015
# Name: JOK
# 
# jonas.kolb@kaba.com
#
#***********************************************************************
# Librarys *************************************************************

import os,sys
import RPi.GPIO as GPIO
from time import sleep
# Library Strommesser
from yocto_api import *
from yocto_current import *
# Library Displaymodule
from Adafruit_CharLCD import Adafruit_CharLCD
# Library Dickes Kabel
import serial

#***********************************************************************
# Grenzwerte (Hier die passenden Werte eintragen) **********************

#ROT in mA
rot_min = 80
rot_max = 130

#GRÜN in mA
gruen_min = 40
gruen_max = 70

#HF in mA
hf_min = 35
hf_max = 65

#***********************************************************************


log_datei = '/home/pi/Adafruit-Raspberry-Pi-Python-Code/Adafruit_CharLCD/testdata.txt'

#***********************************************************************
# Display Module Adafruit **********************************************

lcd = Adafruit_CharLCD() 
# Groesse des Displays festlegen
lcd.begin(16,1)

#***********************************************************************
# Dickes Kabel Serielle Schnittstelle **********************************

dk = serial.Serial('/dev/ttyUSB0', 115200, timeout=2.0, rtscts=False, dsrdtr=False)
# Kontrollinie auf das Logic Level setzen
dk.setDTR(False)
# Flasht Input Buffer
dk.flushInput()
# Löscht Output Buffer
dk.flushOutput()
sleep(0.5)

#***********************************************************************
# Variablen initialisieren und deklarieren *****************************

# Stromspeichervariablen
strom_rot = 0
strom_gruen = 0
strom_hf = 0
# Testvariablen
rot_ok = 0
gruen_ok = 0
hf_ok = 0
bestanden = 0
# Statistikvariablen
ok = 1
n_ok = 0
ruhestrom = 0
flanke = 0
flanke2 = 0
statistik = 0
count = 0

# Switch case 
n = 0

# Speichervariable
save = 1
var = 0
var2 = 0

# Tasterwert zuordnen
reset = 8
back = 7
left = 10
right = 9
start = 11
# Hintergrundbeleuchtung AN/AUS
light = 25

#***********************************************************************
# GPIO setzen **********************************************************

GPIO.setup(reset, GPIO.IN)
GPIO.setup(back, GPIO.IN)
GPIO.setup(left, GPIO.IN)
GPIO.setup(right, GPIO.IN)
GPIO.setup(start, GPIO.IN) 
GPIO.setup(light, GPIO.OUT)
GPIO.output(25, GPIO.HIGH)

#***********************************************************************
# Stromsensor initialisieren *******************************************

# Nachricht auf Konsole und Display
print("Initialisieren")
lcd.message(" Initialisieren")

# Suchpfad angeben
errmsg=YRefParam()
YAPI.RegisterHub("usb",errmsg)

# Stromsensor anhander der Seriennummer finden
current = YCurrent.FindCurrent("YAMPMK01-3CA5A.current1")

# Weiterfahren wenn Stromsensor bereit ist
if current.isOnline():
	
#***********************************************************************	
# Main *****************************************************************
#***********************************************************************
	
	f=open(log_datei,'a' if os.path.exists(log_datei) else 'w')
	f.write("DATALOG\n")
	f.close()

	# Endlosschlaufe
	while 1: 
	
#***********************************************************************
# "Switch case" ********************************************************

				# Menüauswahl
				if n == 0:
					lcd.setCursor(0, 0)
					lcd.message("    Auswahl:    ")
					# Nach links oder rechts?
					if GPIO.input(left) == GPIO.LOW:
						# Vom aktuellen Punkt eins links
						if save < 4:
							save = save + 1
						else:
							save = 1
					if GPIO.input(right) == GPIO.LOW:
						# Vom aktuellen Punkt eins rechts
						if save > 1:
							save = save - 1
						else:
							save = 4
							
					# Da sich n immer ändert gibt es save
					n = save
				# Test starten	
				elif n == 1:
					save = 1
					n = 0
					lcd.setCursor(0, 1)
					lcd.message("  Test starten  ")
					if GPIO.input(start) == GPIO.LOW:
						lcd.clear()
						n = 5
						
				# Statistik		
				elif n == 2:
					save = 2
					n = 0
					lcd.setCursor(0, 1)
					lcd.message("   Statistik    ")
					if GPIO.input(start) == GPIO.LOW:
						lcd.clear()
						n = 6
						
				# Einstellungen		
				elif n == 3:
					save = 3
					n = 0
					lcd.setCursor(0, 1)
					lcd.message(" Einstellungen  ")
					if GPIO.input(start) == GPIO.LOW:
						lcd.clear()
						n = 7
				# Info		
				elif n == 4:
					save = 4
					n = 0
					lcd.setCursor(0, 1)
					lcd.message("      Info      ")
					if GPIO.input(start) == GPIO.LOW:
						lcd.clear()
						n = 8
						
				# Test starten 2
				elif n == 5:
				# ROT
					# Rot LED ein
					print "rot ein"
					dk.write('\x7E\xF1\x14\x01\x5C\xF3\x7E')
					sleep(0.8)
					strom_rot = int(current.get_currentValue())
					# Rot LED aus
					while strom_rot <= 30:
						dk.write('\x7E\xF1\x14\x01\x5C\xF3\x7E')
						sleep(0.2)
						# Strom auslesen
						strom_rot = int(current.get_currentValue())
						count = count +1
						if count >= 10: break							
					count = 0
					sleep(0.8)
					strom_rot = int(current.get_currentValue())	
					print "rot aus"
					dk.write('\x7E\xF1\x14\x00\xD5\xE2\x7E')
					sleep(0.05)
				# GRÜN
					# Grün LED ein
					dk.write('\x7E\xF1\x14\x03\x4E\xD0\x7E')
					sleep(0.8)	
					# Strom auslesen
					strom_gruen = int(current.get_currentValue())
					# Grün LED aus
					dk.write('\x7E\xF1\x14\x02\xC7\xC1\x7E')
					sleep(0.05)
				# HF
					# RFID ein
					dk.write('\x7E\xF1\x11\x01\xE4\x8D\x7E')
					sleep(0.05)
					# HF RFID ein
					dk.write('\x7E\xF1\x11\x03\xF6\xAE\x7E')
					sleep(0.8)
					# Strom auslesen
					strom_hf = int(current.get_currentValue())
					sleep(0.1)
					# Werte mit Grenzwerte überprüfen
					# Rot
					if strom_rot < rot_max and strom_rot > rot_min:
						rot_ok = 1
					else: 
						rot_ok = 0
					
					# Grün	
					if strom_gruen < gruen_max and strom_gruen > gruen_min:
						gruen_ok = 1
					else: 
						gruen_ok = 0	
					
					# HF
					if strom_hf < hf_max and strom_hf > hf_min:
						hf_ok = 1
					else: 
						hf_ok = 0
					
					# Ströme an Display ausgeben
					lcd.clear()
					lcd.setCursor(0, 1)
					lcd.message((str(strom_rot)) + 'mA')
					lcd.setCursor(6, 1)
					lcd.message((str(strom_gruen)) + 'mA')
					lcd.setCursor(12, 1)
					lcd.message((str(strom_hf)) + 'mA')
					
					if rot_ok == 1 and gruen_ok == 1 and hf_ok == 1:
					# Test bestanden
						
						f=open(log_datei,'a' if os.path.exists(log_datei) else 'w')
						f.write('{} {:3}mA {:3}mA {:3}mA\n'.format('pass', strom_rot, strom_gruen, strom_hf))            						
						f.close()
						
						# Statistik ausrechnen
						ok = ok + 1	
						lcd.setCursor(1, 0)
						lcd.message("Test bestanden")
						# Grün LED ein
						dk.write('\x7E\xF1\x14\x03\x4E\xD0\x7E')
						# Hintergrundbeleuchtung blinken
						GPIO.output(25, GPIO.LOW)
						sleep(0.4)
						GPIO.output(25, GPIO.HIGH)
						sleep(0.4)
					else:
					# Test nicht bestanden
						f=open(log_datei,'a' if os.path.exists(log_datei) else 'w')
						f.write('{} {:3}mA {:3}mA {:3}mA\n'.format('fail', strom_rot, strom_gruen, strom_hf))
						f.close()
						
						n_ok = n_ok + 1
						# Rot LED ein
						dk.write('\x7E\xF1\x14\x01\x5C\xF3\x7E')
						lcd.setCursor(0, 0)
						lcd.message(" Test nicht OK")
						sleep(1)
						lcd.setCursor(0, 1)
						lcd.message(" START --> EXIT ")
						while GPIO.input(start) == GPIO.HIGH:
							sleep(0.01)	
					# Knaufwechsel auffordern	
					lcd.setCursor(0, 1)
					lcd.message(" Beenden: back  ")
					
					# Auswahlmenü starten
					n = 9
					
				# Statistik 2
				elif n == 6:
					# Statistik Prozentzahl ausrechnen
					statistik = int((float(ok) / float(ok + n_ok)) * 100.0)
					lcd.setCursor(0, 0)
					lcd.message((str(statistik)) + '% bestanden')
					lcd.setCursor(0, 1)
					lcd.message("reset ---> clear")
					# Statistik mit reset löschen
					if GPIO.input(reset) == GPIO.LOW:
						ok = 1
						n_ok = 0 
					if GPIO.input(back) == GPIO.LOW:
						n = 0
					sleep(0.1)
						
				# Einstellungen 2
				elif n == 7:
					# Grenzwerte auf Display ausgeben
					lcd.setCursor(0, 0)
					lcd.message('R '+ str(rot_min) +'.'+ str(rot_max))
					lcd.setCursor(9, 0)
					lcd.message('G '+ str(gruen_min) +'.'+ str(gruen_max))
					lcd.setCursor(0, 1)
					lcd.message('H '+ str(hf_min) +'.'+ str(hf_max))
					lcd.setCursor(9, 1)
					lcd.message("R 15.22")
					sleep(0.1)
					if GPIO.input(back) == GPIO.LOW:
						n = 0
						
				# Info 2
				elif n == 8:
					lcd.setCursor(0, 0)
					lcd.message("Firmware: V1.1")
					lcd.setCursor(10, 1)
					lcd.message("by JOK")
					sleep(0.1)
					if GPIO.input(back) == GPIO.LOW:
						n = 0
				# Knauf wechseln		
				elif n == 9:
					# Ruhestrom auslesen
					ruhestrom = int(current.get_currentValue())
					print ruhestrom
					sleep(0.1)
					# Negative Flankenerkennung des Stroms
					if ruhestrom < 4:
						flanke = 1
						print "flanke1"	
					if ruhestrom > 5 and flanke == 1:
						flanke2 = 1
						
					# Positive Flankenerkennung des Stroms
					if flanke2 == 1:
						print "flanke2"
						flanke = 0
						flanke2 = 0
						lcd.clear()
						lcd.setCursor(0, 0)
						lcd.message("  Test startet  ")
						
						dk.flushInput()
						dk.flushOutput()
						sleep(0.5)
						# Test erneut starten
						n = 5
					# Test abbrechen
					if GPIO.input(back) == GPIO.LOW:
						n = 0
				# Fehler abfangen
				else:
					n = 0	
					
#***********************************************************************
					
				# 10ms Zeitverzögerung
				sleep(0.01)
