import RPi.GPIO as GPIO          
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # Sử dụng BCM pin numbers

ENA = 16 #steering
ENB = 13 #throttle

m11 = 20
m12 = 21
m21 = 19
m22 = 26

def motor_init():
    global pwm_ENA 
    global pwm_ENB 
    
    GPIO.setup(ENA, GPIO.OUT, initial=GPIO.HIGH)  
    GPIO.setup(ENB, GPIO.OUT, initial=GPIO.HIGH)

    GPIO.setup(m11, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(m12, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(m21, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(m22, GPIO.OUT, initial=GPIO.LOW)

   
    pwm_ENA = GPIO.PWM(ENA, 2000)
    pwm_ENB = GPIO.PWM(ENB, 2000)
    pwm_ENA.start(0)
    pwm_ENB.start(0)

def cleanup():
    GPIO.cleanup()

def stop():
    print('Stop')
    GPIO.output(m11, 0)
    GPIO.output(m12, 0)
    GPIO.output(m21, 0)
    GPIO.output(m22, 0)
    pwm_ENA.ChangeDutyCycle(0)
    pwm_ENB.ChangeDutyCycle(0)

def forward():
    GPIO.output(m11, 1)
    GPIO.output(m12, 0)
    GPIO.output(m21, 1)
    GPIO.output(m22, 0)
    pwm_ENA.ChangeDutyCycle(75)   
    pwm_ENB.ChangeDutyCycle(75)
    print('Forward')

def right():
    GPIO.output(m11, 0)
    GPIO.output(m12, 0)
    GPIO.output(m21, 1)
    GPIO.output(m22, 0)
    pwm_ENA.ChangeDutyCycle(75)
    pwm_ENB.ChangeDutyCycle(75)
    print('Right')

def left():
    GPIO.output(m11, 1)
    GPIO.output(m12, 0)
    GPIO.output(m21, 0)
    GPIO.output(m22, 0)
    pwm_ENA.ChangeDutyCycle(75)
    pwm_ENB.ChangeDutyCycle(75)
    print('Left')
    
def spin_left():
    GPIO.output(m11, 0)
    GPIO.output(m12, 1)
    GPIO.output(m21, 1)
    GPIO.output(m22, 0)
    pwm_ENA.ChangeDutyCycle(75)
    pwm_ENB.ChangeDutyCycle(75)
    print('left')

#turn right in place
def spin_right():
    GPIO.output(m11, 1)
    GPIO.output(m12, 0)
    GPIO.output(m21, 0)
    GPIO.output(m22, 1)
    pwm_ENA.ChangeDutyCycle(75)
    pwm_ENB.ChangeDutyCycle(75)
    print('Right')


def forward_with_speed(sqd):
    GPIO.output(m11, 1)
    GPIO.output(m12, 0)
    GPIO.output(m21, 1)
    GPIO.output(m22, 0)
    pwm_ENA.ChangeDutyCycle(sqd)  
    pwm_ENB.ChangeDutyCycle(sqd)  
    #pwm_ENB.start(sqd)
    print('Forward with speed')


if __name__ == "__main__":
    motor_init() 
    forward()    
    sleep(5)
    # left()       
    # sleep(2)
    right()
    sleep(2)
    #forward()
    #sleep(5)
    spin_right()
    sleep(2)
    stop()        
    cleanup()     





