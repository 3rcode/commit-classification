import csv
import pandas as pd


path = "/var/data/CG/new_try/data/matrix-org_synapse/pr_info.csv"
pr_info = pd.read_csv(path, engine="python", on_bad_lines="skip")
print(pr_info.info())
