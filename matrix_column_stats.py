"""Column statistics of a random integer matrix.

Converted from a Google Colab / Jupyter notebook to a plain Python script.

Steps:
  1. Build an N x N matrix (list of lists) of random integers in [0, 100).
  2. Compute the mean of each column:      m = sum(a_i) / N
  3. Plot the column means (line plot and bar plot).
  4. Compute the standard deviation of each column:
                                           std = sqrt(sum((a_i - m)^2) / N)
  5. Compute the variance of each column:  var = std^2

Note on building the matrix: writing N*[N*[0]] does NOT give N independent
rows. It creates one inner list and N references to it, so changing one row
changes them all. That is why each row is created separately below.
"""

import random as rd

import numpy as np
import matplotlib.pyplot as plt

N = 100  # dimension of the matrix

# --- Generate random square matrix of integers ---------------------------
Ran_lis = N * [0]  # a list of N zeros
for i in range(N):  # replace each 0 with its own new list of N zeros
    Ran_lis[i] = N * [0]

for i in range(N):
    for j in range(N):
        Ran_lis[i][j] = rd.randrange(0, 100)

print(Ran_lis)  # view list for confirmation

# --- Mean value of each column -------------------------------------------
Mean_lis = N * [0]
for j in range(N):
    meanv = 0
    for i in range(N):
        meanv += Ran_lis[i][j]
    Mean_lis[j] = meanv / N

print(Mean_lis)

# --- Data visualisation ---------------------------------------------------
plt.figure(figsize=(10, 10))
plt.plot(Mean_lis)
plt.title("Mean Value")
plt.show()

plt.figure(figsize=(10, 10))
plt.bar(range(N), Mean_lis)
plt.title("Bar Plot")
plt.show()

# --- Standard deviation of each column -----------------------------------
SD_list = N * [0]
for j in range(N):
    sd = 0
    for i in range(N):
        zeta = Ran_lis[i][j] - Mean_lis[j]
        sd += zeta * zeta
    SD_list[j] = float(np.sqrt(sd / N))

print(SD_list)

# --- Variance of each column ---------------------------------------------
# The notebook ended with this heading but no code; this completes it.
Var_list = [sd * sd for sd in SD_list]

print(Var_list)
