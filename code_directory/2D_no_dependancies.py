from copy import deepcopy
import math
import tkinter

# important contacts
G = 1  # temporary value
delta_time = 1
# store both last and new global states as a dictionary. Each entry in these dictionaries is as follows:
# dictionary = {obj_name: [obj_mass, obj_x_pos, obj_y_pos, obj_x_vel, obj_y_vel]}
last_frame_state = {}
new_frame_state = {}


def calculate_next_frame():
    global last_frame_state, new_frame_state
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
    last_frame_state = deepcopy(new_frame_state)


# Test situation
last_frame_state = {
    "obj1": [10, 10, 0, 0, 0],
    "obj2": [10, -10, 0, 0, 0]
}

calculate_next_frame()
calculate_next_frame()
calculate_next_frame()
