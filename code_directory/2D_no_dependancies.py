import math
import tkinter

# important variables
delta_time = 10
scale = 1
x_avg = 0
y_avg = 0
# Constant
G = 6.67408e-11
# store the global state as a dictionary. Each entry in this dictionary is as follows:
# dictionary = {obj_name: [obj_mass, obj_x_pos, obj_y_pos, obj_x_vel, obj_y_vel]}
global_state = {}

# store the last 10 positions of each object in a dictionary
location_history = {}

# Test situation
test_start_state = {
    "obj1": [1e10, 10, 0, 0, 0],
    "obj2": [1e10, -10, 0, 0, 0],
    # "obj3": [1e10, 0, 10, 0, -0.0125],
}
global_state = test_start_state


def update_state():
    # The following function takes the current frame information state and calculates the next
    def calculate_next_frame(last_frame_state):
        new_frame_state = {}
        for object1_name in last_frame_state:
            print(f"main object: {object1_name}")
            object1_properties = last_frame_state[object1_name]
            print("properties", object1_properties)
            obj1_mass, obj1_x_pos, obj1_y_pos, obj1_x_vel, obj1_y_vel = object1_properties
            # Calculate new position = old position + old velocity * delta time
            new_x_pos = obj1_x_pos + obj1_x_vel * delta_time
            print("new_x_pos", new_x_pos)
            new_y_pos = obj1_y_pos + obj1_y_vel * delta_time
            print("new_y_pos", new_y_pos)
            x_acc = 0
            y_acc = 0
            # Calculate acceleration
            for object2_name in last_frame_state:
                if object1_name != object2_name:
                    print(f"reference object: {object2_name}")
                    object2_properties = last_frame_state[object2_name]
                    print("properties", object2_properties)
                    obj2_x_pos, obj2_y_pos = object2_properties[1], object2_properties[2]
                    # the gravitational force per unit mass formula is Gm/r**2 in the direction of the object
                    # calculate the force by using the formula while taking the object2 as the center
                    delta_x = obj1_x_pos - obj2_x_pos
                    print("delta-x", delta_x)
                    delta_y = obj1_y_pos - obj2_y_pos
                    print("delta_y", delta_y)
                    acc_value = G * obj1_mass / (delta_y**2 + delta_x**2)
                    print("acc_value", acc_value)
                    # now the angle
                    try:
                        angle = math.atan(delta_y/delta_x)
                    except ZeroDivisionError:
                        angle = math.pi/2 * (1 if delta_y > 0 else -1)
                    if delta_x < 0:  # to account for the full 360 degrees
                        angle += math.pi
                    print("angle", angle)
                    # now the components, the negative sign is because gravity is an attractive force
                    x_acc += -acc_value * math.cos(angle)
                    print("x_acc", x_acc)
                    y_acc += -acc_value * math.sin(angle)
                    print("y_acc", y_acc)

            # Calculate new velocity = old velocity + acceleration * delta time
            new_x_vel = obj1_x_vel + x_acc * delta_time
            print("new_x_vel", new_x_vel)
            new_y_vel = obj1_y_vel + y_acc * delta_time
            print("new_y_vel", new_y_vel)

            new_frame_state[object1_name] = [obj1_mass, new_x_pos, new_y_pos, new_x_vel, new_y_vel]

        print(new_frame_state)
        return new_frame_state

    global global_state
    global_state = calculate_next_frame(global_state)


def update_display():
    global global_state, main_display, x_avg, y_avg, scale
    radius = 1
    # Find centre point and scale
    for object_name in global_state:
        object_properties = global_state[object_name]
        obj_x_pos = object_properties[1]
        obj_y_pos = object_properties[2]
        try:
            x_max = max(x_max, obj_x_pos)
            x_min = min(x_min, obj_x_pos)
            y_max = max(y_max, obj_y_pos)
            y_min = min(y_min, obj_y_pos)
        except UnboundLocalError:
            x_max = x_min = obj_x_pos
            y_max = y_min = obj_y_pos
    print("min-max", x_max, x_min, y_max, y_min)
    x_avg = (x_max + x_min)/len(global_state)
    y_avg = (y_max + y_min)/len(global_state)
    main_display.update()
    win_height = main_display.winfo_height()
    win_width = main_display.winfo_width()
    print("win", win_height, win_width)
    # The 2*radius is so than 2 circles at each end would be in frame
    scale = min(win_width/(x_max - x_min + 2*radius + 10), win_height/(y_max - y_min + 2*radius + 10))
    print("centre point", x_avg, y_avg)
    print("scale", scale)

    # draw the objects
    main_display.delete("all")
    zero_y_coord = win_height/2 + y_avg * scale  # the negative is because in Tkinter y increases downwards
    zero_x_coord = win_width/2 - x_avg * scale
    print("zero coords", zero_x_coord, zero_y_coord)
    main_display.create_line(0, zero_y_coord, win_width, zero_y_coord)  # x-axis
    main_display.create_line(zero_x_coord, 0, zero_x_coord, win_height)  # y-axis
    for object_name in global_state:
        object_properties = global_state[object_name]
        obj_x_rel_pos = object_properties[1] - x_avg
        obj_y_rel_pos = object_properties[2] - y_avg
        print("rel pos", obj_x_rel_pos, obj_y_rel_pos)
        x0 = (obj_x_rel_pos - radius)*scale + win_width/2  # left-most point
        x1 = (obj_x_rel_pos + radius)*scale + win_width/2  # right-most point
        y0 = win_height/2 - (obj_y_rel_pos - radius)*scale  # bottom-most point (least negative y as tkinter increases y downwards)
        y1 = win_height/2 - (obj_y_rel_pos + radius)*scale  # top-most point (most negative y as tkinter decreases y downwards)
        print(x0, x1, y0, y1)
        main_display.create_oval(x0, y0, x1, y1, fill="red")


def main_update():
    update_state()
    update_display()


main_window = tkinter.Tk()
main_window.geometry("1000x600+100+100")
main_window.title("2D simulation of the Newtonian model of gravity")

next_frame_button = tkinter.Button(main_window, text="Next frame", command=main_update)
next_frame_button.pack(side="bottom", fill="x")

main_display = tkinter.Canvas(main_window)
main_display.pack(fill="both", expand=True)


update_display()
main_window.mainloop()
