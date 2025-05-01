import RPi.GPIO as GPIO                    #Import GPIO library
import time
import main_motor as mM 


led = 22


mM.motor_init()

EchoPin = 23
TrigPin = 24
#GPIO.setup(key,GPIO.IN)
GPIO.setup(EchoPin,GPIO.IN)
GPIO.setup(TrigPin,GPIO.OUT)

def Distance():
    count = 0
    flag = 0
    while True:
        avgDistance = 0
        for i in range(5):
            GPIO.output(TrigPin, False)
            time.sleep(0.1)

            GPIO.output(TrigPin, True)
            time.sleep(0.00001)
            GPIO.output(TrigPin, False)

            while GPIO.input(EchoPin) == 0:
                pass
            pulse_start = time.time()

            while GPIO.input(EchoPin) == 1:
                pass
            pulse_end = time.time()

            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150
            distance = round(distance, 2)
            avgDistance += distance

        avgDistance = avgDistance / 5
        print(avgDistance)

        if avgDistance < 25:
            count += 1
            mM.stop()
            time.sleep(1)
            time.sleep(1.5)

            if (count % 3 == 1) and (flag == 0):
                mM.right()
                flag = 1
            else:
                mM.left()
                flag = 0

            time.sleep(1.5)
            mM.stop()
            time.sleep(1)
        else:
            mM.forward()
            flag = 0


try:
    
    Distance()  # Bắt đầu đo khoảng cách và di chuyển
except KeyboardInterrupt:
        pass
        
pwm_ENA.stop()
pwm_ENB.stop()
GPIO.cleanup()

