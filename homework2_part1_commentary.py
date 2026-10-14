# Homework II - Part 1
# Commentary on class code

# Our imports
# We use "as" for abbreviation and easier module-library access
import random as rd

import numpy as np  # used later for np.sqrt in Part 4 (standard deviation)
import matplotlib.pyplot as plt

# Now the code part
# We start by setting the dimension of the matrix we aim to build
N = 100

# The code is then split into 5 parts, each having its own functionality

# Part 1: Generation of random square matrix of integers
Ran_lis = N * [0]  # we create a list of N zeros
for i in range(N):  # we then replace each 0 with its own new list of N zeros
    Ran_lis[i] = N * [0]
# the idea here is for Ran_lis to work as a 2D matrix (a grid) conceptually speaking
# the zeros are placeholders: Python cannot assign to a list position that does
# not exist yet, so the slots have to be created first and filled afterwards
# each row is built separately inside the loop on purpose: writing N * [N * [0]]
# would put the SAME inner list in every slot, so changing one row would change all rows

# we fill the matrix with random integers in a specified range
for i in range(N): # i for matrix rows
    for j in range(N): # j for matrix columns
        Ran_lis[i][j] = rd.randrange(0, 100)  # random integer from 0 to 99 (100 is excluded)

print(Ran_lis)  # we view our list

# Part 2: Mean value of each column
Mean_lis = N * [0] # a list of N values, one mean for each column of the matrix
for j in range(N): # j to target the matrix columns
    meanv = 0 # reset the sum to zero for every column, so each column starts fresh
    for i in range(N): # for every row
        meanv += Ran_lis[i][j] # sum the values to the meanv
    Mean_lis[j] = meanv / N # calculate the mean for the specific column

print(Mean_lis) # print the whole list of means

# Part 3: Visualization of our data
# TODO: explain what is plotted, the difference between the two charts,
#       and what they show
plt.figure(figsize=(10, 10))
plt.plot(Mean_lis)
plt.title("Mean Value")
plt.show()

plt.figure(figsize=(10, 10))
plt.bar(range(N), Mean_lis)
plt.title("Bar Plot")
plt.show()

#Part 4: Standard deviation of each column
#Part 5: Variance of each column
