import math
import tkinter

# important variables
delta_time = 1
scale = 1
centre_point = [0, 0]
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
            # Calculate new position = old position + old velocity * delta time
            new_x_pos = object1_properties[1] + object1_properties[3] * delta_time
            print("new_x_pos", new_x_pos)
            new_y_pos = object1_properties[2] + object1_properties[4] * delta_time
            print("new_y_pos", new_y_pos)
            x_acc = 0
            y_acc = 0
            # Calculate acceleration
            for object2_name in last_frame_state:
                if object1_name != object2_name:
                    print(f"reference object: {object2_name}")
                    object2_properties = last_frame_state[object2_name]
                    print("properties", object2_properties)
                    # the gravitational force per unit mass formula is Gm/r**2 in the direction of the object
                    # calculate the force by using the formula while taking the object2 as the center
                    delta_x = object1_properties[1] - object2_properties[1]
                    print("delta-x", delta_x)
                    delta_y = object1_properties[2] - object2_properties[2]
                    print("delta_y", delta_y)
                    acc_value = G * object1_properties[0] / (delta_y**2 + delta_x**2)
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
            new_x_vel = object1_properties[3] + x_acc * delta_time
            print("new_x_vel", new_x_vel)
            new_y_vel = object1_properties[4] + y_acc * delta_time
            print("new_y_vel", new_y_vel)

            new_frame_state[object1_name] = [object1_properties[0], new_x_pos, new_y_pos, new_x_vel, new_y_vel]

        print(new_frame_state)
        return new_frame_state

    global global_state
    global_state = calculate_next_frame(global_state)


def update_display():
    global global_state, main_display, centre_point, scale
    # Find centre point and scale
    x_max = 0
    y_max = 0
    x_min = 0
    y_min = 0
    for object_name in global_state:
        object_properties = global_state[object_name]
        x_max = max(x_max, object_properties[1])
        x_min = min(x_min, object_properties[1])
        y_max = max(y_max, object_properties[2])
        y_min = min(y_min, object_properties[2])
    print(x_max, x_min, y_max, y_min)
    x_avg = (x_max + x_min)/len(global_state)
    y_avg = (y_max + y_min)/len(global_state)
    main_display.update()
    # Height is actually the x direction. Width is y space.
    win_height = main_display.winfo_height()
    win_width = main_display.winfo_width()
    print("win", win_height, win_width)
    # Y is negative in the following 2 lines because I want +ve y to be up
    centre_point = [x_avg + win_width/2, -y_avg + win_height/2]
    scale = min(win_width/(x_max - x_min + 40), win_height/(y_min - y_max + 40))
    print("centre point", centre_point)
    print("scale", scale)

    # draw the objects
    radius = 1
    index = 0
    main_display.delete("all")
    for object_name in global_state:
        object_properties = global_state[object_name]
        x0 = (object_properties[1]-radius)*scale+centre_point[0]
        x1 = (object_properties[1]+radius)*scale+centre_point[0]
        y0 = (object_properties[2]-radius)*scale+centre_point[1]
        y1 = (object_properties[2]+radius)*scale+centre_point[1]
        print(x0, x1, y0, y1)
        main_display.create_line(centre_point[0]-100*scale, centre_point[1], centre_point[0]+100*scale, centre_point[1])
        main_display.create_line(centre_point[0], centre_point[1]-100*scale, centre_point[0], centre_point[1]+100*scale)
        main_display.create_oval(x0, y0, x1, y1, fill="red")
        index += 1

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
