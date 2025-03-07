import pyvisa as visa
import time

rm=visa.ResourceManager()
li=rm.list_resources()
for index in range(len(li)):
    print(str(index)+" - "+li[index])
choice = input("Which device?: ")
vi=rm.open_resource(li[int(choice)])

print(vi.query("*idn?"))

RANGE = 10
SLOWRATE = 0
COUNT = 2
STEP = 83
LEVEL = 5
WIDTH = 0.05
SLEW = 0.1

# Create another list
# setup list
vi.write(f"list:range {RANGE}")
vi.write(f"list:slow {SLOWRATE}")
vi.write(f"list:count {COUNT}")
vi.write(f"list:step {STEP}")

# Set the values
for i in range(1, STEP + 1):
    vi.write(f"list:level {i}, {LEVEL}")
    vi.write(f"list:width {i}, {WIDTH}")

# Save to slot 2
vi.write("list:save 2")

# Print List out
vi.write("list:rcl 2")
print("Number of steps: ", vi.query("list:step?"))
print("Slow slew?: ", vi.query("list:slow?"))
print("Repeat count: ", vi.query("list:count?"))
for i in range(1,6,1):
    step = "list:level? "+str(i)
    width = "list:width? "+str(i)
    print("Step ",str(i), " level: ",vi.query(step), "Width: ", vi.query(width))


print("Run list 2")
vi.write("list:rcl 2")
vi.write("func:mode list")
print(vi.query("func:mode?"))
vi.write("trigger:source bus")
print(vi.query("trigger:source?"))
vi.write("input on")
vi.write("*trg")
time.sleep(10)
vi.write("input off")
vi.write("func:mode fix")

