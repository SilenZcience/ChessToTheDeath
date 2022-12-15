import numpy as np

chess_values = np.array([1,3,3,5,9]) #p,n,b,r,q - actual chess values

quantity = np.array([8, 2, 2, 2, 1]) 
attack_values = np.array([120, 45, 32, 15, 60])
health_values = np.array([120, 32, 45, 90, 10])
#King Hp/Dmg = 150/35
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

chess_value = normalized_value * chess_values
print("chess value:", chess_value)

chess_value_diff = chess_value - (1/9)*max(chess_value)*chess_values
print("chess value difference:", chess_value_diff)

print("Attacks, 'til death:")
hits_to_death = np.ceil(health_values.reshape(-1, 1).repeat(attack_values.shape[0], axis=1) / attack_values)
print(hits_to_death)