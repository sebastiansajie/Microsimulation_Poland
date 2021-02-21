"""
app00.py illustrates use of TPRU-India taxcalc release 2.0.0
USAGE: python app00.py > app00.res
CHECK: Use your favorite Windows diff utility to confirm that app00.res is
       the same as the app00.out file that is in the repository.
"""
import pandas as pd
import matplotlib.pyplot as plt
import string
from taxcalc import *

# create Records object containing pit.csv and pit_weights.csv input data
recs = Records()

grecs = GSTRecords()

# create CorpRecords object using cross-section data
crecs1 = CorpRecords(data='cit_poland.csv', weights='cit_weights_poland.csv')
# Note: weights argument is optional
assert isinstance(crecs1, CorpRecords)
assert crecs1.current_year == 2017

# create Policy object containing current-law policy
pol = Policy()

# specify Calculator objects for current-law policy
calc1 = Calculator(policy=pol, records=recs, corprecords=crecs1,
                   gstrecords=grecs, verbose=False)

# NOTE: calc1 now contains a PRIVATE COPY of pol and a PRIVATE COPY of recs,
#       so we can continue to use pol and recs in this script without any
#       concern about side effects from Calculator method calls on calc1.

assert isinstance(calc1, Calculator)
assert calc1.current_year == 2017

np.seterr(divide='ignore', invalid='ignore')

# Produce DataFrame of results using cross-section
calc1.calc_all()
#sector=calc1.carray('sector')

dump_vars = ['CIT_ID_NO', 'legal_form', 'sector', 'province', 'small_business', 'revenue', 'expenditure', 'income', 'tax_free_income_total', 'tax_base_before_deductions', 'deductions_from_tax_base',
             'income_tax_base_after_deductions', 'tax_free_income_statistic_purpose_art_17_1_4d_etc', 'citax']
dumpdf = calc1.dataframe_cit(dump_vars)
dumpdf['ID_NO']= "A"+ dumpdf['CIT_ID_NO'].astype('str')
weight = calc1.carray('weight')
dumpdf['weight'] = weight
dumpdf['weighted_citax'] = dumpdf['weight']*dumpdf['citax']
#print(dumpdf)
dumpdf.to_csv('app00_poland1.csv', index=False, float_format='%.0f')

pol2 = Policy()
#reform = Calculator.read_json_param_objects('tax_incentives_benchmark.json', None)
reform = Calculator.read_json_param_objects('tax_incentives_benchmark.json', None)

#reform = Calculator.read_json_param_objects('app01_reform.json', None)

"""
thisdict = reform
list(thisdict.items())[0]
list(thisdict.items())[1]
list(thisdict.items())[2]
list(thisdict.items())[3]
list(thisdict.items())[4]
list(thisdict.items())[5]
"""

ref_dict = reform['policy']
var_list = []
tax_expenditure_var_list = []
for pkey, sdict in ref_dict.items():
        #print(f'pkey: {pkey}')
        #print(f'sdict: {sdict}')
        for k, s in sdict.items():
            reform.pop("policy")
            mydict={}
            mydict[k]=s
            mydict0={}
            mydict0[pkey]=mydict
            reform['policy']=mydict0
            print('reform:', reform)
            #print(f'k: {k}')
            #print(f's: {s}')
            pol2.implement_reform(reform['policy'])

            calc2 = Calculator(policy=pol2, records=recs, corprecords=crecs1,
                               gstrecords=grecs, verbose=False)
            calc2.calc_all()
            dump_vars = ['CIT_ID_NO', 'tax_free_income_statistic_purpose_art_17_1_4d_etc', 'tax_free_income_total', 'citax']
            dumpdf_2 = calc2.dataframe_cit(dump_vars)
            #dumpdf_2.to_csv('app00_poland'+k+'.csv', index=False, float_format='%.0f')
            dumpdf_2['ID_NO']= "A"+ dumpdf_2['CIT_ID_NO'].astype('int').astype('str')
            dumpdf_2.drop('CIT_ID_NO', axis=1, inplace=True)
            dumpdf_2 = dumpdf_2.rename(columns={'citax':'citax'+k})
            dumpdf = pd.merge(dumpdf, dumpdf_2, how="inner", on="ID_NO")
            dumpdf["weighted_citax"+k] = dumpdf["citax"+k]*dumpdf['weight']
            dumpdf["tax_expenditure" +k+"_mill"] = (dumpdf["weighted_citax"+k] - dumpdf['weighted_citax'])/10**6
            var_list = var_list + [k]

            #print(dumpdf)

dumpdf.to_csv('tax_expenditures_poland_detailed.csv', index=False, float_format='%.0f')

tax_expenditure_var_list = ["tax_expenditure"+i+"_mill" for i in var_list]
with open('taxcalc/current_law_policy_poland.json') as f:
    current_law_policy = json.load(f)
tax_expenditure_desc_english = [string.capwords(current_law_policy[i]['description']) for i in var_list]
tax_expenditure_desc_polish = [string.capwords(current_law_policy[i]['long_name']) for i in var_list]
dumpdf_english = dumpdf.rename(columns=dict(zip(tax_expenditure_var_list, tax_expenditure_desc_english)), inplace=False)
dumpdf_polish = dumpdf.rename(columns=dict(zip(tax_expenditure_var_list, tax_expenditure_desc_polish)), inplace=False)

dumpdf_tax_expenditures_english = dumpdf_english[tax_expenditure_desc_english].sum(axis=0).to_frame()
dumpdf_tax_expenditures_english = dumpdf_tax_expenditures_english.round(decimals=1)
dumpdf_tax_expenditures_english = dumpdf_tax_expenditures_english.reset_index()
dumpdf_tax_expenditures_english.columns=['Tax Expenditure', 'Estimate (mill Zlotys)']
dumpdf_tax_expenditures_english.to_csv('tax_expenditures_poland_english.csv', index=False, float_format='%.0f')

dumpdf_tax_expenditures_polish = dumpdf_polish[tax_expenditure_desc_polish].sum(axis=0).to_frame()
dumpdf_tax_expenditures_polish = dumpdf_tax_expenditures_polish.round(decimals=1)
dumpdf_tax_expenditures_polish = dumpdf_tax_expenditures_polish.reset_index()
dumpdf_tax_expenditures_polish.columns=['Tax Expenditure', 'Estimate (mill Zlotys)']
dumpdf_tax_expenditures_polish.to_csv('tax_expenditures_poland_polish.csv', index=False, float_format='%.0f')


df_sector = dumpdf_1.groupby(['sector']).sum()
df_sector['citax_millions'] = df_sector['citax']/10**6

df_province = dumpdf_1.groupby(['province']).sum()
df_province['citax_millions'] = df_province['citax']/10**6

df_small_business = dumpdf_1.groupby(['small_business']).sum()
df_small_business['citax_millions'] = df_small_business['citax']/10**6

cmap = plt.cm.tab10
colors = cmap(np.arange(len(df_sector)) % cmap.N)

ax = df_sector.plot(kind='bar', use_index=True, y='citax_millions', 
                    legend=False, rot=90,
                    figsize=(8,8), color=colors)

ax.set_ylabel('CIT in million Zlotys')
ax.set_xlabel('')
ax.set_title(' CIT collection by sector (2017)', fontweight="bold")
plt.show()

cmap = plt.cm.tab10
colors = cmap(np.arange(len(df_province)) % cmap.N)

ax = df_province.plot(kind='bar', use_index=True, y='citax_millions', 
                    legend=False, rot=90,
                    figsize=(8,8), color=colors)
ax.set_ylabel('CIT in million Zlotys')
ax.set_xlabel('')
ax.set_title(' CIT collection by Province (2017)', fontweight="bold")
plt.show()

cmap = plt.cm.tab10
colors = cmap(np.arange(len(df_province)) % cmap.N)

ax = df_small_business.plot(kind='bar', use_index=True, y='citax_millions', 
                    legend=False, rot=90,
                    figsize=(8,8), color=colors)
ax.set_ylabel('CIT in million Zlotys')
ax.set_xlabel('')
ax.set_title(' CIT collection by Type of Business (2017)', fontweight="bold")
plt.show()


