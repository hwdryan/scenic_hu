import matplotlib.pyplot as plt

# Lists to store data
time_values = []
speed_values = []
x_values = []
y_values = []
throttle = []

# Read the data from the file
with open("Zhijing_scenario/parameters_log.txt", "r") as file:
    for line in file:
        # Split each line into three values
        values = list(map(float, line.strip().split(', ')))
        time_values.append(values[0])  
        speed_values.append(values[1])
        x_values.append(values[2])
        y_values.append(values[3])
        throttle.append(values[4])

# Calculate the distance traveled
distance_values = [0]  # Initial distance is 0
for i in range(1, len(x_values)):
    distance = ((x_values[i] - x_values[i-1])**2 + (y_values[i] - y_values[i-1])**2)**0.5
    distance_values.append(distance_values[-1] + distance)

t0 = time_values[0]
time_values = [x-t0 for x in time_values]  

# Calculate acceleration
acceleration_values = [0]  # Initial acceleration is set to 0
for i in range(1, len(speed_values)):
    delta_speed = speed_values[i] - speed_values[i-1]
    delta_time = time_values[i] - time_values[i-1]

    # Avoid division by zero
    if delta_time != 0:
        acceleration = delta_speed / delta_time
        acceleration_values.append(acceleration)
    else:
        acceleration_values.append(0)

# Plotting the line graph
plt.figure(1)
plt.plot(time_values, distance_values, label='Distance Traveled')
plt.xlabel('Time')
plt.ylabel('Distance')
plt.legend()
plt.show()

# Plotting the line graph
plt.figure(2)
plt.plot(time_values, speed_values, label='speed_values')
plt.xlabel('Time')
plt.ylabel('speed_values')
plt.legend()
plt.show()

# Plotting the line graph
plt.figure(3)
plt.plot(time_values, acceleration_values, label='acceleration_values')
plt.xlabel('Time')
plt.ylabel('acceleration_values')
plt.legend()
plt.show()

# Plotting the line graph
plt.figure(4)
plt.plot(throttle, acceleration_values, label='acceleration_values')
plt.xlabel('Time')
plt.ylabel('acceleration_values')
plt.legend()
plt.show()

