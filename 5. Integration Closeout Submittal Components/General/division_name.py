# from pandas import read_excel
# import os
#
# def get_division_name(specification_number,app_path):
#
#     location=os.path.join(app_path,'master.xlsx')
#
#     master=read_excel(location,sheet_name="Spec Divisions")
#     if specification_number[0]=='0':
#         division=int(specification_number[1])
#     else:
#         division=int(specification_number[:2])
#
#     division=specification_number[:2]+" - "+master.loc[master['Specification Group'] == division, 'Name'].iloc[0]
#     return division