import pandas as pd

xls = pd.ExcelFile("Gen_AI Dataset.xlsx")
print(xls.sheet_names)
