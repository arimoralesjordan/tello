import tello
from tello_control_ui import TelloUI


def main():

    drone = tello.Tello('', 8889, False, .3, '10.0.1.24')
    vplayer = TelloUI(drone, "./img")

    # start the Tkinter mainloop
    vplayer.root.mainloop()


if __name__ == "__main__":
    main()
