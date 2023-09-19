import math
import tkinter

# Reference values
G = 6.67408e-11
max_object_num = 10
# Default settings
delta_time = 10000
scale = 1
x_avg = 0
y_avg = 0
history_record_length = 100
centre_mode = "geometrical"
absolute_scale = False  # When False recalculate scale, otherwise use the global. The name shadowing is INTENTIONAL

# store the global state as a dictionary. Each entry in this dictionary is as follows:
# global_state = {obj_name: [[obj_mass, [obj_x_pos, obj_y_pos, obj_x_vel, obj_y_vel], "colour", radius]}
global_state = {}
# store the last history_record_length positions of each object in a dictionary
# location_history = {obj_name: [[oldest x, oldest y], [next x, next y], ....., [last x, last y]]}
location_history = {}

# Test cases
test_case_1 = {  # Earth-Moon-sun system (recommended delta_time 10000)
    "Sun": [1.989e30, [0, 0, 0, 0], "yellow", 10000000000],
    "Earth": [5.9722e24, [1.5037e11, 0, 0, 29780], "blue", 300000000],
    "Moon": [7.34767e22, [1.507544e11, 0, 0, 30802], "grey", 100000000]
}
test_case_2 = {  # direct collision (recommended delta_time 5)
    "Obj1": [1e10, [10, 0, 0, 0], "red", 1],
    "Obj2": [1e10, [-10, 0, 0, 0], "blue", 1],
}
test_case_3 = {  # double orbit (recommended delta_time 5)
    "Obj1": [1e10, [20, 0, 0, -0.08], "red", 1],
    "Obj2": [1e10, [-20, 0, 0, 0.08], "blue", 1],
}

global_state = test_case_1


# The following function takes the current frame information state and calculates the next
def update_state():
    global global_state
    print("CALC NEW FRAME ---------------------------------------")
    new_frame_state = {}
    for object1_name in global_state:
        print(f"main object: {object1_name}")
        obj1_x_pos, obj1_y_pos, obj1_x_vel, obj1_y_vel = global_state[object1_name][1]
        # Calculate new position = old position + old velocity * delta time
        new_x_pos = obj1_x_pos + obj1_x_vel * delta_time
        print("new_x_pos", new_x_pos)
        new_y_pos = obj1_y_pos + obj1_y_vel * delta_time
        print("new_y_pos", new_y_pos)

        # Calculate acceleration
        x_acc = 0
        y_acc = 0
        for object2_name in global_state:
            if object1_name != object2_name:
                print(f"reference object: {object2_name}")
                obj2_x_pos, obj2_y_pos = global_state[object2_name][1][:2]
                # the gravitational force per unit mass formula is Gm/r**2 in the direction of the object
                # calculate the force by using the formula while taking the object2 as the center
                delta_x = obj1_x_pos - obj2_x_pos
                print("delta-x", delta_x)
                delta_y = obj1_y_pos - obj2_y_pos
                print("delta_y", delta_y)
                acc_value = G * global_state[object2_name][0] / (delta_y ** 2 + delta_x ** 2)
                print("acc_value", acc_value)
                # now the angle
                try:
                    angle = math.atan(delta_y / delta_x)
                except ZeroDivisionError:
                    angle = math.pi / 2 * (1 if delta_y > 0 else -1)
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

        new_frame_state[object1_name] = [global_state[object1_name][0], [new_x_pos, new_y_pos, new_x_vel, new_y_vel],
                                         global_state[object1_name][-2], global_state[object1_name][-1]]

        # store the position history
        obj_pos_his = location_history.setdefault(object1_name, [])
        while len(obj_pos_his) > history_record_length - 1:
            obj_pos_his.pop(0)
        obj_pos_his.append([new_x_pos, new_y_pos])
        print("loc his", location_history)

    print(new_frame_state)
    global_state = new_frame_state


def update_display():
    print("UPDATE DISPLAY ---------------------------------------------------")
    global main_display
    # Find "geometrical" centre point and scale
    object_names = list(global_state.keys())
    # set starting x, y and radius values for this calculation
    first_object_name = object_names.pop(0)
    x_max = x_min = global_state[first_object_name][1][0]
    y_max = y_min = global_state[first_object_name][1][1]
    largest_radius = global_state[first_object_name][-1]
    # now compare with the rest. Remember that we popped the first
    for object_name in object_names:
        obj_x_pos, obj_y_pos = global_state[object_name][1][:2]
        x_max = max(x_max, obj_x_pos)
        x_min = min(x_min, obj_x_pos)
        y_max = max(y_max, obj_y_pos)
        y_min = min(y_min, obj_y_pos)
        largest_radius = max(largest_radius, global_state[object_name][-1])
    print("min-max", x_max, x_min, y_max, y_min)
    print("largest radius", largest_radius)
    if centre_mode == "origin":
        global x_avg, y_avg
    elif centre_mode == "geometrical":
        x_avg = (x_max + x_min) / 2
        y_avg = (y_max + y_min) / 2
    elif centre_mode == "centre of mass":
        pass  # TODO: IMPLEMENT
    main_display.update()
    win_height = main_display.winfo_height()
    win_width = main_display.winfo_width()
    print("win", win_height, win_width)
    if absolute_scale:
        global scale
    else:
        # The 3*radius is so that 2 circles at each end would be in frame and
        # an extra half radius on both sides as padding
        scale = min(win_width / (x_max - x_min + 3 * largest_radius),
                    win_height / (y_max - y_min + 3 * largest_radius))
    print("centre point", x_avg, y_avg)
    print("scale", scale)

    # draw to canvas
    main_display.delete("all")
    # Find the zero line axes
    zero_y_coordinate = win_height / 2 + y_avg * scale  # the positive y_avg is because in Tkinter y increases downwards
    zero_x_coordinate = win_width / 2 - x_avg * scale
    print("zero coordinates", zero_x_coordinate, zero_y_coordinate)
    # Draw them
    main_display.create_line(0, zero_y_coordinate, win_width, zero_y_coordinate)  # x-axis
    main_display.create_line(zero_x_coordinate, 0, zero_x_coordinate, win_height)  # y-axis
    # Draw objects and their paths
    for object_name in global_state:
        # Draw objects
        print(object_name)
        object_numbers = global_state[object_name][1][:2]
        object_colour = global_state[object_name][-2]
        radius = global_state[object_name][-1]
        obj_x_rel_pos = object_numbers[0] - x_avg
        obj_y_rel_pos = object_numbers[1] - y_avg
        print("rel pos", obj_x_rel_pos, obj_y_rel_pos)
        x0 = (obj_x_rel_pos - radius) * scale + win_width / 2  # left-most point
        x1 = (obj_x_rel_pos + radius) * scale + win_width / 2  # right-most point
        y0 = win_height / 2 - (obj_y_rel_pos + radius) * scale  # bottom-most point
        y1 = win_height / 2 - (obj_y_rel_pos - radius) * scale  # top-most point
        print("circle coordinate x0, x1 then y0, y1", x0, x1, y0, y1)
        main_display.create_oval(x0, y0, x1, y1, fill=object_colour)

        # Draw path from location history
        object_history = location_history[object_name]
        print("obj his", object_history)
        x0 = (object_history[0][0] - x_avg) * scale + win_width / 2
        y0 = win_height / 2 - (object_history[0][1] - y_avg) * scale
        print("starting coordinate in line", x0, y0)
        for i in range(1, len(object_history)):
            x1 = (object_history[i][0] - x_avg) * scale + win_width / 2
            y1 = win_height / 2 - (object_history[i][1] - y_avg) * scale
            print("next coordinate in line", x1, y1)
            main_display.create_line(x0, y0, x1, y1, fill=object_colour)
            x0, y0 = x1, y1


def main_update():
    update_state()
    update_display()


def toggle_settings():
    global settings_toggle, settings_frame
    if settings_toggle:
        settings_toggle = False
        settings_frame.pack_forget()
    else:
        settings_toggle = True
        settings_frame.pack(side="right", fill="both", expand=True)
    update_display()
    print("settings_toggle", settings_toggle)


def reset_location_history():
    print("current global state", global_state)
    for object_name in global_state:
        print("resetting locations history for", object_name)
        location_history[object_name] = [global_state[object_name][1][:2].copy()]
    print("reset loc his", location_history)


# PROGRAM START
# first set the starting positions to object history by resetting it
reset_location_history()

main_window = tkinter.Tk()
main_window.geometry("1000x600+100+100")
main_window.title("2D simulation of the Newtonian model of gravity")

button_frame = tkinter.Frame(main_window)
button_frame.pack(side="bottom", fill="x")
settings_toggle = False
settings_button = tkinter.Button(button_frame, text="Settings", command=toggle_settings)
settings_button.pack(side="right", fill="x")
next_frame_button = tkinter.Button(button_frame, text="Next frame", command=main_update)
next_frame_button.pack(side="left", fill="x", expand=True)

main_display = tkinter.Canvas(main_window)
main_display.pack(side="left", fill="both", expand=True)
settings_frame = tkinter.Frame(main_window)

# test settings:
# absolute_scale = True
# centre_mode = "zero"

update_display()
main_window.mainloop()
