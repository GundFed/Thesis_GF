# -*- coding: utf-8 -*-
"""
Remove ONLY EXACT TEXT duplicates,
AND ONLY for sender == 'Āgenskalna klīnika'

User messages are untouched.
"""

import pandas as pd

sarunas_path = r"C:\Users\JurisFedotovs\Desktop\RTU\MASTER\Āgenskalna_klīnika_sarunas\EXPERIMENT\CODE_BASE\DATA\01_anonymized_messages.csv"
main_path    = r"C:\Users\JurisFedotovs\Desktop\RTU\MASTER\Āgenskalna_klīnika_sarunas\EXPERIMENT\CODE_BASE\DATA\Āgenskalna_klīnika-main.csv"
output_clean = r"C:\Users\JurisFedotovs\Desktop\RTU\MASTER\Āgenskalna_klīnika_sarunas\EXPERIMENT\CODE_BASE\DATA\02_delete_dubicates.csv"


TEXT_COL = "content"
SENDER_COL = "sender"
TARGET_SENDER = "Āgenskalna klīnika"

##### Load data #####
df_sarunas = pd.read_csv(sarunas_path, encoding="utf-8-sig", dtype=str).fillna("")
df_main    = pd.read_csv(main_path,    encoding="utf-8-sig", dtype=str).fillna("")

##### Strip whitespace #####
df_sarunas[TEXT_COL] = df_sarunas[TEXT_COL].str.strip()
df_main[TEXT_COL]    = df_main[TEXT_COL].str.strip()

df_sarunas[SENDER_COL] = df_sarunas[SENDER_COL].str.strip()
df_main[SENDER_COL]    = df_main[SENDER_COL].str.strip()

##### Filter main dataset - only speciffic sender #####
df_main_clinic = df_main[df_main[SENDER_COL] == TARGET_SENDER].copy()

##### Create set of exact clinic comment texts #####
clinic_exact_set = set(df_main_clinic[TEXT_COL])

print(f"Clinic messages in main: {len(df_main_clinic)}")
print(f"Unique clinic texts:     {len(clinic_exact_set)}")

##### Mark duplicates if text matches and sender is Āgenskalna klīnika or Edgars Mednis  #####
df_sarunas["is_exact_clinic_dup"] = (
    (df_sarunas[SENDER_COL] == TARGET_SENDER) &
    (df_sarunas[TEXT_COL].isin(clinic_exact_set))
)

##### Extract duplicates #####
df_duplicates = df_sarunas[df_sarunas["is_exact_clinic_dup"]].copy()


##### Remove duplicates #####
df_clean = df_sarunas[~df_sarunas["is_exact_clinic_dup"]].copy()
df_clean = df_clean.drop(columns=["is_exact_clinic_dup"])

##### Save cleaned version #####
df_clean.to_csv(output_clean, index=False, encoding="utf-8-sig")

##### Output #####
print()
print("     Dublicates removed  ")
print()
print(f"Sarunas total rows:         {len(df_sarunas)}")
print(f"Clinic rows in main:        {len(df_main_clinic)}")
print(f"Exact clinic duplicates:    {len(df_duplicates)}")
print(f"Remaining rows after clean: {len(df_clean)}")
print()
print(f"Cleaned file saved to:\n {output_clean}")
print()
print("DONE")
