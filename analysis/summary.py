#!/usr/bin/python3

import sqlite3
import numpy as np

experiments = ["idle", "redis", "postgresql", "wordpress"]
implementations = ["native", "multidocker", "ssl"]

conn = sqlite3.connect("energy.sqlite")
c = conn.cursor()


def get_average_power(exp):
  energy = [0.0, 0.0, 0.0] # same order as [implementations]

  print("\n")
  print(exp)


  for j, implementation in enumerate(implementations):
    if exp != "postgresql" and implementation == "ssl":
      continue

    c.execute("SELECT * FROM energy WHERE experiment = '{}' AND configuration = '{}'".format(exp, implementation))
    data = np.array(c.fetchall())
    average = np.zeros(len(data))
    for i, row in enumerate(data):
      # average[i] = float(row[3]) / float(row[6])*1000
      average[i] = float(row[3])
    

    energy[j] = np.mean(average)
    print(implementation + " -> " + str(energy[j]))

  percent_difference = (energy[1] - energy[0]) / energy[0] * 100
  print("Percent Difference = " + str(percent_difference))

  return energy

energy = get_average_power("idle")
print("Benchmark: Idle for ten minutes")
print("Scaled: Idle for one week")
print([x / 600 * 86400 * 7 for x in energy])
print([x / 600 * 86400 * 7 /1000 * 0.000277778 * 6.76 / 100 for x in energy])

energy = get_average_power("wordpress")
# print("Benchmark: Idle for ten minutes")
# print("Scaled: Idle for 24h")
# print([x / 600 * 86400 for x in energy])
# print([x / 600 * 86400 /1000 * 0.000277778 * 6.76 for x in energy])

energy = get_average_power("redis")
print("Benchmark: 1,500,000 queries")
print("Scaled: 1,000,000,000 queries")
print([x / 1500000 * 1000000000 for x in energy])
print([x / 1500000 * 1000000000 /1000 * 0.000277778 * 6.76 / 100 for x in energy])

energy = get_average_power("postgresql")
print("Benchmark: 1000 Transactions")
print("Scaled: 1,000,000 Transactions")
print([x / 1000 * 1000000 for x in energy])
print([x / 1000 * 1000000 /1000 * 0.000277778 * 6.76 / 100 for x in energy])

