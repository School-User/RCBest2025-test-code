# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       aiden                                                        #
# 	Created:      9/20/2025, 12:57:51 PM                                       #
# 	Description:  V5 project - Improved Codebase                               #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
from vex import *

# --- Configuration ---
# You can adjust these values to tune your robot's performance
DRIVE_DEADBAND = 5  # Ignore joystick inputs below this threshold to prevent drift
ARM_SPEED_PERCENT = 75 # Default speed for arm movements
CLAW_OPEN_DEGREES = 0   # Define the degrees for your small arm/claw open
CLAW_CLOSE_DEGREES = 90 # Define the degrees for your small arm/claw closed
BIG_ARM_UP_DEGREES = 100 # Example for big arm position
BIG_ARM_DOWN_DEGREES = 0 # Example for big arm position

# --- Robot Initialization ---
# Brain should be defined by default
brain = Brain()
controller = Controller(PRIMARY) # Specify PRIMARY controller

# Drive Motors
# For drive motors, it's often better to group them for simpler control.
# If you have 4 drive motors, you might create a MotorGroup for left and right side.
# Assuming a 2-motor drive system for now.
left_motor = Motor(Ports.PORT5, GearSetting.RATIO_18_1, True) # True for reversed if needed
right_motor = Motor(Ports.PORT6, GearSetting.RATIO_18_1, False) # False for not reversed, or vice-versa

# Arm Motors
big_arm_motor = Motor(Ports.PORT10, GearSetting.RATIO_18_1, False)
small_arm_motor = Motor(Ports.PORT9, GearSetting.RATIO_18_1, False) # Often called a 'claw' or 'grabber'

# Set brake type for arms to hold position
big_arm_motor.set_stopping(HOLD)
small_arm_motor.set_stopping(HOLD)

# --- Helper Functions for Arm Control ---
# It's good practice to encapsulate specific actions into functions
# For arm movements, using position control is often more reliable than just velocity

def big_arm_set_position(target_degrees, velocity_percent=ARM_SPEED_PERCENT):
    """Moves the big arm to a specific target degree."""
    big_arm_motor.set_velocity(velocity_percent, PERCENT)
    big_arm_motor.spin_to_position(target_degrees, DEGREES, True) # True to wait for completion

def small_arm_set_position(target_degrees, velocity_percent=ARM_SPEED_PERCENT):
    """Moves the small arm (claw) to a specific target degree."""
    small_arm_motor.set_velocity(velocity_percent, PERCENT)
    small_arm_motor.spin_to_position(target_degrees, DEGREES, True)

def big_arm_grab():
    """Example: If 'big arm' is actually a large claw, this would close it."""
    # For a continuous big arm, this might be to a specific 'pickup' angle
    # For now, let's assume it means move to a specific position
    big_arm_set_position(BIG_ARM_UP_DEGREES) # Example: move to an 'up' position
    brain.screen.print_line(1, "Big Arm Grab/Up")

def big_arm_release():
    """Example: If 'big arm' is actually a large claw, this would open it."""
    # For a continuous big arm, this might be to a specific 'drop' angle
    big_arm_set_position(BIG_ARM_DOWN_DEGREES) # Example: move to a 'down' position
    brain.screen.print_line(1, "Big Arm Release/Down")

def small_arm_grab():
    """Closes the small arm/claw to grab an object."""
    small_arm_set_position(CLAW_CLOSE_DEGREES)
    brain.screen.print_line(2, "Small Arm Grab")

def small_arm_release():
    """Opens the small arm/claw to release an object."""
    small_arm_set_position(CLAW_OPEN_DEGREES)
    brain.screen.print_line(2, "Small Arm Release")

# --- Main Robot Control Loop ---
# Flags for enabling/disabling parts of the code
enable_driver_control = True
enable_debug_screen = False # Set to True to see joystick values on screen

# Reset motor encoders for accurate position control
big_arm_motor.set_position(0, DEGREES)
small_arm_motor.set_position(0, DEGREES)


# Initial arm states (optional, but good for starting position)
small_arm_release() # Start with claw open
big_arm_release() # Start big arm down/at base


# This is your main loop that runs continuously during the match
while enable_driver_control:
    # Get joystick positions
    axis1 = controller.axis1.position() # Right joystick X
    axis2 = controller.axis2.position() # Right joystick Y
    axis3 = controller.axis3.position() # Left joystick Y
    axis4 = controller.axis4.position() # Left joystick X

    # --- Drive Control (Arcade Drive using left joystick for Y, right for X) ---
    # Using a "deadband" to prevent motors from drifting due to tiny joystick movements
    drive_forward_backward = 0
    if abs(axis3) > DRIVE_DEADBAND:
        drive_forward_backward = axis3

    drive_turn = 0
    if abs(axis1) > DRIVE_DEADBAND: # Using axis1 for turning (right stick X)
        drive_turn = axis1

    # Calculate motor velocities for arcade drive
    # Positive `drive_turn` for turning right, negative for turning left
    left_drive_velocity = drive_forward_backward + drive_turn
    right_drive_velocity = drive_forward_backward - drive_turn

    # Set drive motor velocities
    left_motor.set_velocity(left_drive_velocity, PERCENT)
    right_motor.set_velocity(right_drive_velocity, PERCENT)

    # Spin motors (they will continue at this velocity until changed)
    left_motor.spin(FORWARD)
    right_motor.spin(FORWARD)

    # --- Big Arm Control (using Axis2 - Right joystick Y) ---
    # Only control big arm if joystick is moved beyond deadband
    if abs(axis2) > DRIVE_DEADBAND:
        big_arm_motor.set_velocity(axis2, PERCENT)
        big_arm_motor.spin(FORWARD) # Spin based on joystick direction
    else:
        big_arm_motor.stop() # Stop the arm when joystick is released (HOLD will maintain position)

    # --- Button Control for Arms/Claws ---
    # Big Arm Grab/Release
    if controller.buttonR1.pressing():
        big_arm_grab()
        wait(200, MSEC) # Debounce: prevent multiple presses from one quick tap

    if controller.buttonR2.pressing():
        big_arm_release()
        wait(200, MSEC) # Debounce

    # Small Arm/Claw Grab/Release
    # Note: You had both L1 for grab and L1 for release, which is a bug.
    # Changed to L1 for grab, L2 for release.
    if controller.buttonL1.pressing():
        small_arm_grab()
        wait(200, MSEC) # Debounce

    if controller.buttonL2.pressing(): # Corrected button for release
        small_arm_release()
        wait(200, MSEC) # Debounce

    # --- Debugging Information on Brain Screen ---
    if enable_debug_screen:
        brain.screen.clear_screen() # Clear entire screen for fresh display
        brain.screen.set_cursor(1, 1)
        brain.screen.print("L_Drive: {} R_Drive: {}".format(left_drive_velocity, right_drive_velocity))
        brain.screen.set_cursor(2, 1)
        brain.screen.print("Big Arm: {} Small Arm: {}".format(big_arm_motor.position(DEGREES), small_arm_motor.position(DEGREES)))
        brain.screen.set_cursor(3, 1)
        brain.screen.print("Axis1: {} Axis2: {} Axis3: {} Axis4: {}".format(axis1, axis2, axis3, axis4))


    # Small delay to prevent the loop from consuming 100% CPU and allow other processes
    wait(20, MSEC)

# The code below this point will only run if 'enable_driver_control' becomes False
# This is usually for autonomous modes or specific testing outside the main driver loop.
# In a typical competition, your autonomous code would go here or in a separate function.