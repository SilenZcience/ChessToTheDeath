import numpy as np

chess_values = np.array([1,3,3,5,9]) #p,n,b,r,q - actual chess values

quantity = np.array([8, 2, 2, 2, 1]) 
attack_values = np.array([20, 35, 25, 20, 50])
health_values = np.array([35, 90, 115, 120, 60])

avg_attack_values = 0
for x in zip(quantity, attack_values):
    avg_attack_values += x[0] * x[1]
avg_attack_values = avg_attack_values / sum(quantity)
print("avg attack:", avg_attack_values)

avg_health_values = 0
for x in zip(quantity, health_values):
    avg_health_values += x[0] * x[1]
avg_health_values = avg_health_values / sum(quantity)
print("avg health:", avg_health_values)


normalized_attack_values = (attack_values/avg_health_values)/np.linalg.norm(attack_values/avg_health_values)
print("norm attack:", normalized_attack_values)

normalized_health_values = (health_values/avg_attack_values)/np.linalg.norm(health_values/avg_attack_values)
print("norm health:", normalized_health_values)


normalized_value = normalized_attack_values + normalized_health_values
print("norm value:", normalized_value)

val = normalized_value * chess_values
print(val)

val_diff = val - (1/9)*max(val)*chess_values
print(val_diff)
print(attack_values.shape)
print(health_values.reshape(-1, 1).repeat(attack_values[0], axis=1))