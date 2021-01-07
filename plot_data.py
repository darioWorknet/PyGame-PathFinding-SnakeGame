import pandas as pd
import os
import matplotlib.pyplot as plt

# FILE LOCATION
main_path = "D:\Google Drive\PYTHON\SNAKE_GAME_A_STAR"
file_name = 'scores_5000_15.csv'

# LOAD DATAFRAME
df = pd.read_csv(os.path.join(main_path, file_name))

# PLOT DATAFRAME
plt.figure(figsize=(10,6))
plt.hist(df, bins=30)
plt.xlabel('Score')
plt.ylabel('Frecuency')
plt.show()