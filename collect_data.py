import serial
import argparse
import time
import csv
# 0 = Dab
# 1 = James Bond
# 2 = Mermaid
# 3 = Not Dancing
# Increment 1 for PATH_TO_SAVE
# CHANGE USER NAME ACCORDING: LEON, ZX, JOVI, DIX, NAZ, RH

DEFAULT_USER = "LEON"
MOVE = "Dab"
PORT_NO = '/dev/ttyACM0'
TIME = 90

WINDOW_SIZE = 10
SLIDING_WINDOW = 1
NO_OF_CLASSES = 9
ARRAY_SIZE = 6

def positionCalibration(arduino):
    count = 0
    sum = 0
    print("Calibration Now, KEEP STILL THERE")
    time.sleep(1.0)
    start_time = time.time()
    arduino.reset_input_buffer()
    arduino.reset_output_buffer()
    arduino.flush()
    while(time.time()-start_time <3.0):
        count +=1
        msg = arduino.read_until().decode()
        msg = str(msg).strip('\r\n').split(',')
        dataset = []
        for data in msg:
            dataset.append(float(data))
        print(dataset)
        if(dataset[0]+dataset[1]+dataset[2]==0.0):
            sum+=dataset[4]
        else:
            print("Calibration Fail at stationary")
            return False

    stationary_avg = sum/count

    if stationary_avg < 0.1:
        pass
    else:
        return False
    count = 0
    sum = 0
    print("Calibration Now, KEEP 'RIGHT' THERE")
    time.sleep(2)
    arduino.reset_input_buffer()
    arduino.reset_output_buffer()
    arduino.flush()
    start_time = time.time()
    while(time.time()-start_time < 3.0):
        count +=1
        msg = arduino.read_until().decode()
        msg = str(msg).strip('\r\n').split(',')
        dataset = []
        for data in msg:
            dataset.append(float(data))
        print(dataset)
        if(dataset[0]+dataset[1]+dataset[2]==0.0):
            sum+=dataset[5]
        else:
            print("Calibration Fail at Right")
            return False
    right_avg = sum/count
    if right_avg < -0.1:
        pass
    else:
        print("Restart Sensor")
        return False
    count = 0
    sum = 0
    print("Calibration Now, KEEP 'LEFT' THERE")

    time.sleep(2)
    arduino.reset_input_buffer()
    arduino.reset_output_buffer()
    arduino.flush()
    start_time = time.time()
    while(time.time()-start_time < 3.0):
        count +=1
        msg = arduino.read_until().decode()
        msg = str(msg).strip('\r\n').split(',')
        dataset = []
        for data in msg:
            dataset.append(float(data))
        print(dataset)
        if(dataset[0]+dataset[1]+dataset[2]==0.0):
            sum+=dataset[5]
        else:
            print("Calibration Fail at Right")
            return False
    left_avg = sum/count
    if left_avg > 0.1:
        pass
    else:
        print("Restart Sensor")
        return False

    print("Calibration Done")

    return True

def get_arguments():
    """Parse all the arguments provided from the CLI.

    Returns:
      A list of parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Dance-Dance data harvester.")
    parser.add_argument("--user", type=str, default=DEFAULT_USER)
    parser.add_argument("--move", type=str, default=MOVE)
    parser.add_argument("--port", type=str, default=PORT_NO)
    parser.add_argument("--time", type=str, default=TIME)
    return parser.parse_args()

def move_mapping_str_to_int(result):
    result = result.lower()
    if result == 'forward': move = 0
    elif result == 'right': move = 1
    elif result == 'left': move = 2
    elif result == 'reverse': move = 3
    # if result == 'dab': move = 0
    # elif result == 'james_bond': move = 1
    # elif result =='mermaid': move = 2
    # elif result == 'snake': move = 4
    # elif result == 'scarecrow': move = 5
    # elif result == 'pushback': move = 6
    # elif result == 'window360': move = 7
    # elif result == 'cowboy': move = 8
    # elif result == 'move_left': move = 9
    # elif result == 'move_right': move = 10
    # else: move = 3 # Not dancing
    return move

def read_set(arduino):
    output_x = []
    for i in range(WINDOW_SIZE):
        msg = arduino.readline().decode()
        msg = str(msg).strip('\r\n').split(',')
        output_x.append(msg)
    return np.array(output_x)


args = get_arguments()
count  = 0
arduino = serial.Serial(port=args.port, baudrate=115200, timeout=100)
arduino.reset_input_buffer()
arduino.reset_output_buffer()
arduino.flush()

# if not positionCalibration(arduino):
#     print("Exiting App Now")
#     exit()

while(1):
    print(f"You are {args.user} and is record move: {args.move}")
    correct = input("Press Y/N to confirm:")
    if(correct.lower == 'n'):
        print("Relaunch program again")
    else:
        path = str(args.user)+'/'+str(move_mapping_str_to_int(args.move)+1)+'.csv'
        print(path)
        f = open(path, 'w',newline="")
        header = ['AX','AY','AZ','GX','GY','GZ','Result']
        writer = csv.writer(f)
        writer.writerow(header)
        print("COUNTDOWN 5 secs")
        time.sleep(5)
        arduino.reset_input_buffer()
        arduino.reset_output_buffer()
        arduino.flush()
        start = time.time()
        print("START!")
        while(1):
            output = []
            dataset = []
            count+=1
            total_time = time.time()-start
            msg = arduino.readline().decode()
            msg = str(msg).strip('\r\n').split(',')
            for data in msg:
                data = float(data)
                dataset.append(data)
            dataset.append(move_mapping_str_to_int(args.move))
            # write a row to the csv file
            writer.writerow(dataset)

            if count == 100:
                print(msg)
                print(f"Computed Time: {total_time}")
                count = 0
            if (total_time) >float(args.time): break

        # close the file
        f.close()
    print("Collection Done")
    exit(1)
