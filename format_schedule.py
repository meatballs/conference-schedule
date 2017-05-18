import pickle
import numpy as np

with open('definition/conference.bin', 'rb') as file:
   conference = pickle.load(file)

schedule_array = np.loadtxt('definition/schedule.csv', dtype='int', delimiter=',')
print(schedule_array)
