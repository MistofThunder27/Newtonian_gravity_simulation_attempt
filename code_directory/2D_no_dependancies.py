import math
import tkinter

# Reference values
G = 6.67408e-11
max_object_num = 10
# Default settings
delta_time = 10000
history_record_length = 100
centre_reference = "geometrical"
scale_mode = "fit to zoom"
scale_multiplayer = 1

# store the global state as a dictionary. Each entry in this dictionary is as follows:
# global_state = {obj_name: [[obj_mass, [obj_x_pos, obj_y_pos, obj_x_vel, obj_y_vel], "colour", radius]}
global_state = {}
# store the last history_record_length positions of each object in a dictionary
# location_history = {obj_name: [[oldest x, oldest y], [next x, next y], ....., [last x, last y]]}
location_history = {}

# Test cases
test_case_1 = {  # Solar system (recommended delta_time 10000)
    "Sun": [1.989e30, [0, 0, 0, 0], "yellow", 10000000000],
    "Mercury": [3.301e23, [5.8e10, 0, 0, 47000], "brown", 300000000],
    "Venus": [4.867e24, [1.08e11, 0, 0, 35000], "orange", 300000000],
    "Earth": [5.9722e24, [1.5037e11, 0, 0, 29780], "blue", 300000000],
    "Moon": [7.34767e22, [1.507544e11, 0, 0, 30802], "grey", 100000000]
}
test_case_2 = {  # direct collision (recommended delta_time 5)
    "Obj1": [1e10, [10, 0, 0, 0], "red", 1],
    "Obj2": [1e10, [-10, 0, 0, 0], "blue", 1]
}
test_case_3 = {  # double orbit (recommended delta_time 5)
    "Obj1": [1e10, [20, 0, 0, -0.08], "red", 1],
    "Obj2": [1e10, [-20, 0, 0, 0.08], "blue", 1]
}
test_case_4 = {  # three objects (recommended delta_time 5)
    "Obj1": [1e10, [20, 0, 0, -0.08], "red", 1],
    "Obj2": [1e10, [-20, 0, 0, 0.08], "blue", 1],
    "Obj3": [1e10, [0, -20, 0.01, 0], "yellow", 1]
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

        # Calculate acceleration
        x_acc = 0
        y_acc = 0
        for object2_name in global_state:
            if object1_name is not object2_name:
                print(f"reference object: {object2_name}")
                obj2_x_pos, obj2_y_pos = global_state[object2_name][1][:2]
                # the gravitational force per unit mass formula is Gm/r**2 in the direction of the object
                # calculate the force by using the formula while taking the object1 as the center
                delta_x = obj2_x_pos - obj1_x_pos
                print("delta-x", delta_x)
                delta_y = obj2_y_pos - obj1_y_pos
                print("delta_y", delta_y)
                acc_value = G * global_state[object2_name][0] / (delta_y ** 2 + delta_x ** 2)
                print("acc_value", acc_value)
                # now the angle towards object2
                try:
                    angle = math.atan(delta_y / delta_x)
                    if delta_x < 0:  # to account for the full 360 degrees
                        angle += math.pi
                except ZeroDivisionError:
                    angle = math.pi / 2 * (1 if delta_y > 0 else -1)
                print("angle", angle)
                # now the components
                x_acc += acc_value * math.cos(angle)
                print("x_acc", x_acc)
                y_acc += acc_value * math.sin(angle)
                print("y_acc", y_acc)

        new_frame_state[object1_name] = [
            new_x_pos := obj1_x_pos + obj1_x_vel * delta_time,  # new x position
            new_y_pos := obj1_y_pos + obj1_y_vel * delta_time,  # new y position
            obj1_x_vel + x_acc * delta_time,  # new x velocity
            obj1_y_vel + y_acc * delta_time  # new y velocity
        ]
        print(f"new {object1_name} numbers {new_frame_state[object1_name]}")

        # store the position history
        obj_pos_his = location_history.setdefault(object1_name, [])
        while len(obj_pos_his) > history_record_length:
            obj_pos_his.pop(0)
        obj_pos_his.append([new_x_pos, new_y_pos])
        print("loc his", obj_pos_his)

    # save as the new global state
    for object_name in global_state:
        global_state[object_name][1] = new_frame_state[object_name]
    print("new global state", global_state)


def update_display(begrudgingly_necessary_for_resizing_update=None):
    print("UPDATE DISPLAY ---------------------------------------------------")  # TODO: EVERYTHING
    global main_display, centre_reference
    main_display.update()
    win_height = main_display.winfo_height()
    win_width = main_display.winfo_width()
    print("win", win_height, win_width)

    if centre_reference in global_state:
        print("centre:", centre_reference)
        centre_x, centre_y = global_state[centre_reference][1][:2]
        furthest_x = furthest_y = global_state[centre_reference][-1]
        for object_name in global_state:
            if object_name is not centre_reference:  # TODO: is this check necessary?
                obj_x_pos, obj_y_pos = global_state[object_name][1][:2]
                furthest_x = max(furthest_x, math.fabs(obj_x_pos - centre_x) + global_state[object_name][-1])
                furthest_y = max(furthest_y, math.fabs(obj_y_pos - centre_y) + global_state[object_name][-1])

        if scale_mode == "1 meter = 1 pixel":
            scale = 1
        else:  # scale_mode == "auto"
            # The 2* is so that it covers the same distance on both sides
            scale = min(win_width / 2 / furthest_x, win_height / 2 / furthest_y)

    elif centre_reference == "origin":
        print("centre: origin")
        centre_x = centre_y = furthest_x = furthest_y = 0
        for object_name in global_state:
            obj_x_pos, obj_y_pos = global_state[object_name][1][:2]
            furthest_x = max(furthest_x, math.fabs(obj_x_pos) + global_state[object_name][-1])
            furthest_y = max(furthest_y, math.fabs(obj_y_pos) + global_state[object_name][-1])
        print("furthest points at", furthest_x, furthest_y)

        if scale_mode == "1 meter = 1 pixel":
            scale = 1
        else:  # scale_mode == "auto"
            # The 2* is so that it covers the same distance on both sides
            scale = min(win_width / 2 / furthest_x, win_height / 2 / furthest_y)

    elif centre_reference == "geometrical":
        print("centre: geometrical")
        # Find "geometrical" centre point
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
            largest_radius = max(largest_radius, global_state[object_name][-1])  # TODO: radius of furthest?
        print("min-max", x_max, x_min, y_max, y_min)
        print("largest radius", largest_radius)
        centre_x = (x_max + x_min) / 2
        centre_y = (y_max + y_min) / 2

        if scale_mode == "1 meter = 1 pixel":
            scale = 1
        else:  # scale_mode == "auto"
            # The 3*radius is so that 2 circles at each end would be in frame and
            # an extra half radius on both sides as padding
            scale = min(win_width / (x_max - x_min + 2 * largest_radius),
                        win_height / (y_max - y_min + 2 * largest_radius))

    else:  # if centre_reference == "centre of mass":
        print("centre: mass")
        # Find centre of mass
        centre_x = 0
        centre_y = 0
        sum_of_masses = 0
        for object_name in global_state:
            obj_x_pos, obj_y_pos = global_state[object_name][1][:2]
            obj_mass = global_state[object_name][0]
            centre_x += obj_mass * obj_x_pos
            centre_y += obj_mass * obj_y_pos
            sum_of_masses += obj_mass
        centre_x = centre_x / sum_of_masses
        centre_y = centre_y / sum_of_masses

        # Then find the "min"s and "max"es
        furthest_x = furthest_y = 0
        for object_name in global_state:
            obj_x_pos, obj_y_pos = global_state[object_name][1][:2]
            furthest_x = max(furthest_x, math.fabs(obj_x_pos - centre_x) + global_state[object_name][-1])
            furthest_y = max(furthest_y, math.fabs(obj_y_pos - centre_y) + global_state[object_name][-1])

        if scale_mode == "1 meter = 1 pixel":
            scale = 1
        else:  # scale_mode == "auto"
            # The 2* is so that it covers the same distance on both sides
            scale = min(win_width / 2 / furthest_x, win_height / 2 / furthest_y)

    scale *= scale_multiplayer  # to adjust the scale
    print("centre point", centre_x, centre_y)
    print("scale", scale)

    # draw to canvas
    main_display.delete("all")
    # Find the zero line axes  #TODO: add support for grids
    # the positive centre_y is because in Tkinter y increases downwards
    zero_y_coordinate = win_height / 2 + centre_y * scale
    zero_x_coordinate = win_width / 2 - centre_x * scale
    print("zero coordinates", zero_x_coordinate, zero_y_coordinate)
    # Draw them
    main_display.create_line(0, zero_y_coordinate, win_width, zero_y_coordinate, fill="white")  # x-axis
    main_display.create_line(zero_x_coordinate, 0, zero_x_coordinate, win_height, fill="white")  # y-axis
    # Draw objects and their paths
    for object_name in global_state:
        # Draw objects
        print(object_name)
        object_numbers = global_state[object_name][1][:2]
        object_colour, radius = global_state[object_name][-2:]
        obj_x_rel_pos = object_numbers[0] - centre_x
        obj_y_rel_pos = object_numbers[1] - centre_y
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
        x0 = (object_history[0][0] - centre_x) * scale + win_width / 2
        y0 = win_height / 2 - (object_history[0][1] - centre_y) * scale
        print("starting coordinate in line", x0, y0)
        for i in range(1, len(object_history)):
            x1 = (object_history[i][0] - centre_x) * scale + win_width / 2
            y1 = win_height / 2 - (object_history[i][1] - centre_y) * scale
            print("next coordinate in line", x1, y1)
            main_display.create_line(x0, y0, x1, y1, fill=object_colour)
            x0, y0 = x1, y1


def main_update():
    update_state()
    update_display()


def toggle_settings():
    global settings_toggle, settings_frame, centre_reference, scale_mode, scale_multiplayer
    if settings_toggle:
        settings_toggle = False
        settings_frame.destroy()
    else:
        settings_toggle = True
        # settings frame set up
        settings_frame = tkinter.Frame(main_window)
        settings_frame.pack(side="right", fill="both")
        tkinter.Label(settings_frame, text="Settings menu").pack()

        frame1 = tkinter.Frame(settings_frame)
        frame1.pack()
        tkinter.Label(frame1, text="Centre mode").pack(side="left")
        centre_list = ["origin", "geometrical", "centre of mass"] + list(global_state)
        centre_option = tkinter.StringVar()
        centre_option.set(centre_reference)
        centre_reference_selector = tkinter.OptionMenu(frame1, centre_option, *centre_list)
        centre_reference_selector.pack(side="left")

        frame2 = tkinter.Frame(settings_frame)
        frame2.pack()
        tkinter.Label(frame2, text="Scale mode").pack(side="left")
        scale_multiplayer_box = tkinter.Entry(frame2)
        scale_multiplayer_box.insert("end", str(scale_multiplayer))
        scale_multiplayer_box.pack(side="left")
        scale_list = ["1 meter = 1 pixel", "fit to zoom"]
        scale_option = tkinter.StringVar()
        scale_option.set(scale_mode)
        scale_mode_selector = tkinter.OptionMenu(frame2, scale_option, *scale_list)
        scale_mode_selector.pack(side="left")

        settings_button_frame = tkinter.Frame(settings_frame)
        settings_button_frame.pack(side="bottom")

        def apply_settings():
            global centre_reference, scale_mode, scale_multiplayer
            nonlocal centre_option, scale_multiplayer_box, scale_option
            centre_reference = centre_option.get()
            try:
                scale_multiplayer = float(scale_multiplayer_box.get())
            except TypeError:
                pass
            scale_mode = scale_option.get()
            update_display()

        apply_button = tkinter.Button(settings_button_frame, text="Apply settings", command=apply_settings)
        apply_button.pack(side="left")
        objects_button = tkinter.Button(settings_button_frame, text="Objects' properties", command=apply_settings)
        objects_button.pack(side="left")

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

main_display = tkinter.Canvas(main_window, bg="black")
main_display.pack(side="left", fill="both", expand=True)
main_display.bind("<Configure>", update_display)  # update display at every resize
settings_frame = tkinter.Frame(main_window)

# test settings:
# absolute_scale = True
# centre_reference = "origin"
# centre_reference = "mass"
# centre_reference = "Obj1"

update_display()
main_window.mainloop()
