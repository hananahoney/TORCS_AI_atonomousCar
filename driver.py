import msgParser
import carState
import carControl
import pickle


class Driver(object):
    # A driver object for the SCRC

    def __init__(self, stage):

        print("In constructor of the Driver Class :  ", stage)

        self.WARM_UP = 0
        self.QUALIFYING = 1
        self.RACE = 2
        self.UNKNOWN = 3
        self.stage = stage

        # Getting from msgParser File
        self.parser = msgParser.MsgParser()
        # Getting form carState file
        self.state = carState.CarState()

        self.control = carControl.CarControl()

        self.steer_lock = 0.67738
        self.max_speed = 200
        self.prev_rpm = None

        #  Loading model from a file
        with open("steer_predict", "rb") as f:
            self.mp = pickle.load(f)

        self.value = 0
        self.left = 0
        self.right = 0
        self.forward = 0

    def init(self):

        print("--------------------------------------")
        print("In init function of the Driver class ")

        # Return init string with rangefinder angles

        self.angles = [0 for x in range(19)]

        for i in range(5):
            self.angles[i] = -90 + i * 15
            self.angles[18 - i] = 90 - i * 15

        for i in range(5, 9):
            self.angles[i] = -20 + (i - 5) * 5
            self.angles[18 - i] = 20 - (i - 5) * 5

        return self.parser.stringify({'init': self.angles})

    def drive(self, msg):
        print("--------------------------------------")
        print("In drive function of the Driver class ")
        print("--------------------------------------")

        # Calling setFromMsg function of the car State class
        self.state.setFromMsg(msg)
        print("AAAAAAAAAAAAAAAAAAAA")
        print("Data from sensors : ", msg)
        print("AAAAAAAAAAAAAAAAAAAA")

        print("******************")
        print("Set from msg done ")
        print("******************")

        ################################## Applying prediction using the model ############################

        steerValue = self.mp.predict(
            [[self.state.angle, self.state.trackPos, self.state.speedX, self.state.speedY, self.state.speedZ]])
        self.control.setSteer(steerValue[0])

        ##############################################################################################

        self.gear()
        self.speed()

        ################################# Saving data in a file  ######################################

        # f = open("dataSet.csv", "a")
        # data = str(self.state.angle) + "," + str(self.state.trackPos) + "," + str(self.control.steer) + "\n"
        # f.write(data)
        # f.close()

        ###############################################################################################
        value = self.control.toMsg()
        print("SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS")
        print("Value to sent to the sensors : ", value)
        print("SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS")

        return value

    # me
    def on_press(self, key):

        try:
            if key.char == "a":
                # Logic of left movement
                self.left = self.left + 1
                #
                # self.control.setSteer((self.control.steer - 0.00242343242) * 0.5 / self.steer_lock)

            elif key.char == "d":
                # Logic of right movement
                self.right = self.right + 1
                #
                # self.control.setSteer((self.control.steer + 0.00242343242) * 0.5 / self.steer_lock)


        except AttributeError:
            print("Special key pressed")

        print("****************************************")
        print("////////// SOME KEY PRESSED ////////////")
        print("****************************************")

    # me
    def on_release(self, key):
        print('Key released: {0}'.format(key))

    # def steer(self):
    #     print("In steer function ")
    #     angle = self.state.angle
    #     dist = self.state.trackPos
    #
    #     print("Angle : ", angle)
    #     print("Dist  : ", dist)
    #     print("Old value steering -----> ", self.control.steer)
    #
    #     self.control.setSteer((angle - dist * 0.5) / self.steer_lock)
    #
    #     print("New value steering -----> ", self.control.steer)

    def gear(self):
        rpm = self.state.getRpm()
        gear = self.state.getGear()

        if self.prev_rpm == None:
            up = True
        else:
            if self.prev_rpm - rpm < 0:
                up = True
            else:
                up = False

        if up and rpm > 7000:
            gear += 1

        if not up and rpm < 3000:
            gear -= 1

        self.control.setGear(gear)

    def speed(self):
        speed = self.state.getSpeedX()
        accel = self.control.getAccel()

        if speed < self.max_speed:
            print("Accelerating up ---------------------> ")
            accel = accel + 0.2
            if accel > 2.0:
                accel = 2.0
        else:
            print("Accelerating down <------------------- ")
            accel -= 0.2
            if accel < 0:
                accel = 0.0

        self.control.setAccel(accel)

    def onShutDown(self):
        pass

    def onRestart(self):
        pass

    def checkPress(self):
        return self.value

    def Display(self):
        print("Left : ", self.left)
        print("Right :", self.right)
        print("Lock : ", self.steer_lock)
