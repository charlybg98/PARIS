import os

for image_stamp in os.listdir(r'C:\Users\charl\Documents\NNGUI\Carlos\2023-02-05\Full'):
        data_splitted = image_stamp.split()
        print(data_splitted)
        if data_splitted[2] not in os.listdir(r'C:\Users\charl\Documents\NNGUI\Carlos\2023-02-05\Processed'):
                print(data_splitted[2])