import pandas as pd

dump_wb = pd.ExcelFile("data/1/data_assets_dump_partial.xlsx")
print("Dump sheets:", dump_wb.sheet_names)

dict_wb = pd.ExcelFile("data/1/data_assets_dictionary.xlsx")
print("Dict sheets:", dict_wb.sheet_names)

dump_df = dump_wb.parse("Sheet1")
dict_df = dict_wb.parse("Dictionary")

print(dump_df.head())
print(dict_df.head())
