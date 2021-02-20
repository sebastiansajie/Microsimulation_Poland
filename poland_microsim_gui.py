# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 21:27:09 2020

@author: wb305167
"""

import json
from tkinter import *
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

from tkinter import filedialog

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

from taxcalc import *

from PIL import Image,ImageTk

def generate_total_revenues():
    
    global total_revenue_text1
    global reform_revenue_text1
    global selected_year
    
    selected_year=2019
    # create Records object containing pit.csv and pit_weights.csv input data
    recs = Records()
    
    grecs = GSTRecords()
    
    #print(data_filename)
    #print(weights_filename)
    # create CorpRecords object using cross-section data
    crecs1 = CorpRecords(data=data_filename, weights=weights_filename)
    # Note: weights argument is optional
    assert isinstance(crecs1, CorpRecords)
    assert crecs1.current_year == 2017
    
    # create Policy object containing current-law policy
    #policy_filename = 'current_law_policy_poland.json'
    pol = Policy(DEFAULTS_FILENAME=policy_filename)
    
    # specify Calculator objects for current-law policy
    calc1 = Calculator(policy=pol, records=recs, corprecords=crecs1,
                       gstrecords=grecs, verbose=False)
    
    # NOTE: calc1 now contains a PRIVATE COPY of pol and a PRIVATE COPY of recs,
    #       so we can continue to use pol and recs in this script without any
    #       concern about side effects from Calculator method calls on calc1.
    
    assert isinstance(calc1, Calculator)
    assert calc1.current_year == 2017
    
    np.seterr(divide='ignore', invalid='ignore')
    calc1.advance_to_year(selected_year)

        
    # Produce DataFrame of results using cross-section
    calc1.calc_all()
    
    dump_vars = ['CIT_ID_NO', 'legal_form', 'sector', 'province', 'small_business', 'revenue', 'expenditure', 'income', 'tax_base_before_deductions', 'deductions_from_tax_base',
                 'income_tax_base_after_deductions', 'citax']
    dumpdf_1 = calc1.dataframe_cit(dump_vars)
    dumpdf_1.to_csv('app00_poland1.csv', index=False, float_format='%.0f')
    
    Business_Profit1 = calc1.carray('income')
    Tax_Free_Incomes1 = calc1.carray('tax_free_income_total')
    Tax_Base_Before_Deductions1 = calc1.carray('tax_base_before_deductions')
    Deductions1 = calc1.carray('deductions_from_tax_base')
    Tax_Base_After_Deductions1 = calc1.carray('income_tax_base_after_deductions')
    citax1 = calc1.carray('citax')
    weight1 = calc1.carray('weight')
    etr1 = np.divide(citax1, Business_Profit1)
    weighted_etr1 = etr1*weight1.values
    weighted_etr_overall1 = (sum(weighted_etr1[~np.isnan(weighted_etr1)])/
                             sum(weight1.values[~np.isnan(weighted_etr1)]))
    
    wtd_citax1 = citax1 * weight1
    
    citax_collection1 = wtd_citax1.sum()
    
    citax_collection_billions1 = citax_collection1/10**9
    
    citax_collection_str1 = '{0:.2f}'.format(citax_collection_billions1)
    
    print('\n\n\n')
    print('TAX COLLECTION FOR THE YEAR - 2017\n')
    
    print("The CIT Collection in billions is: ", citax_collection_billions1)
    
    total_revenue_text1=""
    l6.config(text=total_revenue_text1)
    
    reform_revenue_text1=""
    l7.config(text=reform_revenue_text1)
    
    total_revenue_text1 = "TAX COLLECTION FOR THE YEAR - " + str(selected_year)+" : "+str(citax_collection_str1)+" bill Zlotys"
    l6.config(text=total_revenue_text1)
    
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
    pic_filename1 = 'CIT Collection 2017.png' 
    plt.savefig(pic_filename1)
    
    """
    img2 = ImageTk.PhotoImage(Image.open(pic_filename1))
    pic.configure(image=img2)
    pic.image = img2
    """
    
    img1 = Image.open(pic_filename1)
    img2 = img1.resize((400, 400), Image.ANTIALIAS)
    img3 = ImageTk.PhotoImage(img2)
    pic.configure(image=img3)
    pic.image = img3
    
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

def apply_policy_change():
    
    global total_revenue_text1
    global reform_revenue_text1
    # create Records object containing pit.csv and pit_weights.csv input data
    recs = Records()
    
    grecs = GSTRecords()
    
    print(data_filename)
    print(weights_filename)
    # create CorpRecords object using cross-section data
    crecs1 = CorpRecords(data=data_filename, weights=weights_filename)
    # Note: weights argument is optional
    assert isinstance(crecs1, CorpRecords)
    assert crecs1.current_year == 2017
    
    # create Policy object containing current-law policy
    pol = Policy()
    
    # specify Calculator objects for current-law policy
    calc1 = Calculator(policy=pol, records=recs, corprecords=crecs1,
                       gstrecords=grecs, verbose=False)
    pol2 = Policy()
    
    global reform
    reform={}
    reform['policy']={}
    updated_year = int(block_widget_dict[1][2].get())
    updated_value = float(block_widget_dict[1][3].get())
    policy_dict = {}
    policy_dict['_'+selected_item]=[updated_value]
    reform['policy'][updated_year]=policy_dict
    print(reform) 
    #reform = Calculator.read_json_param_objects('app01_reform.json', None)
    pol2.implement_reform(reform['policy'])
    
    calc2 = Calculator(policy=pol2, records=recs, corprecords=crecs1,
                       gstrecords=grecs, verbose=False)
    calc2.advance_to_year(updated_year)
    # NOTE: calc1 now contains a PRIVATE COPY of pol and a PRIVATE COPY of recs,
    #       so we can continue to use pol and recs in this script without any
    #       concern about side effects from Calculator method calls on calc1.
    
    assert isinstance(calc1, Calculator)
    assert calc1.current_year == 2017
    
    np.seterr(divide='ignore', invalid='ignore')

    calc1.advance_to_year(updated_year)
    # Produce DataFrame of results using cross-section
    calc1.calc_all()
    
    dump_vars = ['CIT_ID_NO', 'legal_form', 'sector', 'province', 'small_business', 'revenue', 'expenditure', 'income', 'tax_base_before_deductions', 'deductions_from_tax_base',
                 'income_tax_base_after_deductions', 'citax']
    dumpdf_1 = calc1.dataframe_cit(dump_vars)
    dumpdf_1.to_csv('app00_poland1.csv', index=False, float_format='%.0f')
    
    Business_Profit1 = calc1.carray('income')
    Tax_Free_Incomes1 = calc1.carray('tax_free_income_total')
    Tax_Base_Before_Deductions1 = calc1.carray('tax_base_before_deductions')
    Deductions1 = calc1.carray('deductions_from_tax_base')
    Tax_Base_After_Deductions1 = calc1.carray('income_tax_base_after_deductions')
    citax1 = calc1.carray('citax')
    weight1 = calc1.carray('weight')
    etr1 = np.divide(citax1, Business_Profit1)
    weighted_etr1 = etr1*weight1.values
    weighted_etr_overall1 = (sum(weighted_etr1[~np.isnan(weighted_etr1)])/
                             sum(weight1.values[~np.isnan(weighted_etr1)]))
    
    wtd_citax1 = citax1 * weight1
    
    citax_collection1 = wtd_citax1.sum()
    
    citax_collection_billions1 = citax_collection1/10**9
    
    citax_collection_str1 = '{0:.2f}'.format(citax_collection_billions1)
    
    print('\n\n\n')
    print('TAX COLLECTION FOR THE YEAR - 2017\n')
    
    print("The CIT Collection in billions is: ", citax_collection_billions1)
    
    total_revenue_text1 = "TAX COLLECTION FOR THE YEAR - " + str(updated_year)+" : "+str(citax_collection_str1)+" bill Zlotys"
    l6.config(text=total_revenue_text1)
    
    # Produce DataFrame of results using cross-section
    calc2.calc_all()
    
    dump_vars = ['CIT_ID_NO', 'legal_form', 'sector', 'province', 'small_business', 'revenue', 'expenditure', 'income', 'tax_base_before_deductions', 'deductions_from_tax_base',
                 'income_tax_base_after_deductions', 'citax']
    dumpdf_2 = calc2.dataframe_cit(dump_vars)
    dumpdf_2.to_csv('app00_poland2.csv', index=False, float_format='%.0f')
    
    Business_Profit2 = calc2.carray('income')
    Tax_Free_Incomes2 = calc2.carray('tax_free_income_total')
    Tax_Base_Before_Deductions2 = calc2.carray('tax_base_before_deductions')
    Deductions2 = calc2.carray('deductions_from_tax_base')
    Tax_Base_After_Deductions2 = calc2.carray('income_tax_base_after_deductions')
    citax2 = calc2.carray('citax')
    weight2 = calc2.carray('weight')
    etr2 = np.divide(citax2, Business_Profit2)
    weighted_etr2 = etr2*weight2.values
    weighted_etr_overall2 = (sum(weighted_etr2[~np.isnan(weighted_etr2)])/
                             sum(weight2.values[~np.isnan(weighted_etr2)]))
    
    wtd_citax2 = citax2 * weight2
    
    citax_collection2 = wtd_citax2.sum()
    
    citax_collection_billions2 = citax_collection2/10**9
    
    citax_collection_str2 = '{0:.2f}'.format(citax_collection_billions2)
    
    print('\n\n\n')
    print('TAX COLLECTION FOR THE YEAR UNDER REFORM - 2017\n')
    
    print("The CIT Collection in billions is: ", citax_collection_billions2)
    
    reform_revenue_text1 = "TAX COLLECTION UNDER REFORM FOR THE YEAR - " + str(updated_year)+" : "+str(citax_collection_str2)+" bill Zlotys"
    l7.config(text=reform_revenue_text1)
    


def newselection1(event):
    print('selected1:', event.widget.get())

def newselection2(event):
    print('selected2:', event.widget.get())

def input_data_filename():
    global data_filename
    filez = filedialog.askopenfilenames(parent=root,title='Choose a file')
    filename_path = root.tk.splitlist(filez)[0]
    filename_list = filename_path.split('/')
    data_filename = filename_list[-1]
    entry_data_filename.delete(0,END)
    entry_data_filename.insert(0,data_filename)

def input_weights_filename():
    global weights_filename
    filez = filedialog.askopenfilenames(parent=root,title='Choose a file')
    filename_path = root.tk.splitlist(filez)[0]
    filename_list = filename_path.split('/')
    weights_filename = filename_list[-1]
    entry_weights_filename.delete(0,END)
    entry_weights_filename.insert(0,weights_filename)

def input_policy_filename():
    global policy_filename
    filez = filedialog.askopenfilenames(parent=root,title='Choose a file')
    filename_path = root.tk.splitlist(filez)[0]
    filename_list = filename_path.split('/')
    policy_filename = filename_list[-1]
    entry_policy_filename.delete(0,END)
    entry_policy_filename.insert(0,policy_filename)
    

def policy_options():
    global sub_directory
    global policy_filename
    with open(sub_directory+'/'+policy_filename) as f:
        current_law_policy = json.load(f)
    current_law_policy_sorted = dict(sorted(current_law_policy.items()))    
    policy_options_list = []
    for k, s in current_law_policy_sorted.items():
        #print(k)
        #print(current_law_policy[k]['description'])
        #policy_option_list = policy_option_list + [current_law_policy[k]['description']]
        policy_options_list = policy_options_list + [k[1:]]
    return (current_law_policy, policy_options_list)

def policy_reform():
    global reform
    reform={}
    reform['policy']={}
    reform['policy']['_'+selected_item]={}
    updated_year = block_widget_dict[1][2].get()
    updated_value = block_widget_dict[1][3].get()
    reform['policy']['_'+selected_item][updated_year]=[updated_value]
    print(reform)

    
def show_policy_selection(event):
    global selected_value
    global selected_item
    global selected_year    
    global current_law_policy
   
    selected_item = block_widget_dict[1][1].get()
    selected_value = current_law_policy['_'+ selected_item]['value'][0]
    selected_year = current_law_policy['_'+ selected_item]['row_label'][0]    
    block_widget_dict[1][3].delete(0, END)
    block_widget_dict[1][3].insert(END, selected_value)
    block_widget_dict[1][2].delete(0, END)
    block_widget_dict[1][2].insert(END, selected_year)  
    #print('selected_value ', selected_value)
    return
# --- main ---


root = tk.Tk()
root.geometry('1000x600')


reform={}
selected_item = ""
selected_value = ""
selected_year = 2019
sub_directory = "taxcalc"
data_filename = "cit_poland.csv"
weights_filename = "cit_weights_poland1.csv"
policy_filename = "current_law_policy_poland.json"
total_revenue_text1 = ""
reform_revenue_text1 = ""
reform_filename = "app01_reform.json"

# positions

title_pos_x = 0.5
title_pos_y = 0.0

block_1_title_pos_x = 0.1
block_1_title_pos_y = 0.1
block_title_entry_gap_y = 0.05
block_entry_entry_gap_y = 0.05
block_1_entry_x = 0.15
entry_entry_gap_y = 0.05
block_1_entry_1_y = (block_1_title_pos_y+block_title_entry_gap_y)
block_1_entry_2_y = (block_1_entry_1_y+block_entry_entry_gap_y)
block_1_entry_3_y = (block_1_entry_2_y+block_entry_entry_gap_y)
entry_button_gap = 0.05
button_1_pos_x = 0.1
button_1_pos_y = block_1_entry_3_y + entry_button_gap
block_block_gap = 0.1
block_2_entry_1_1_x = 0.03
block_2_title_pos_y = button_1_pos_y + block_block_gap
text_entry_gap = 0.03
block_2_entry_1_1_y = (block_2_title_pos_y+block_title_entry_gap_y+text_entry_gap)
block_2_combo_entry_gap_x = 0.21
block_2_entry_entry_gap_x = 0.04
block_2_entry_1_2_x = block_2_entry_1_1_x + block_2_combo_entry_gap_x
block_2_entry_1_3_x = block_2_entry_1_2_x + block_2_entry_entry_gap_x
button_2_pos_y = block_2_entry_1_1_y + entry_button_gap
button_add_reform_x = block_2_entry_1_3_x + block_2_entry_entry_gap_x + 0.02

root_title=Label(text="Poland Tax Microsimulation Model",
         font = "Calibri 16 bold")
root_title.place(relx = title_pos_x, rely = title_pos_y, anchor = "n")

l1=Label(text="Current Law",
         font = "Calibri 12 bold")
l1.place(relx = block_1_title_pos_x, rely = block_1_title_pos_y, anchor = "w")

entry_data_filename = Entry(root,width=30)
entry_data_filename.place(relx = block_1_entry_x, 
                          rely = block_1_entry_1_y,
                          anchor = "e")
entry_data_filename.insert(END, data_filename)
button_data_filename = ttk.Button(text = "Change Data File", command=input_data_filename)
button_data_filename.place(relx = block_1_entry_x,
                           rely = block_1_entry_1_y, anchor = "w")
#button.place(x=100,y=50)

entry_weights_filename = Entry(root,width=30)
entry_weights_filename.place(relx = block_1_entry_x,
                             rely = block_1_entry_2_y, anchor = "e")
entry_weights_filename.insert(END, weights_filename)
button_weights_filename = ttk.Button(text = "Change Weights File", command=input_weights_filename)
button_weights_filename.place(relx = block_1_entry_x, 
                              rely = block_1_entry_2_y, anchor = "w")

entry_policy_filename = Entry(root,width=30)
entry_policy_filename.place(relx = block_1_entry_x, 
                            rely = block_1_entry_3_y, anchor = "e")
entry_policy_filename.insert(END, policy_filename)
button_policy_filename = ttk.Button(text = "Change Policy File", command=input_policy_filename)
button_policy_filename.place(relx = block_1_entry_x, 
                             rely = block_1_entry_3_y, anchor = "w")

button_genenerate_revenue_curr_law = ttk.Button(text = "Generate Current Law Total Revenues", command=generate_total_revenues)
button_genenerate_revenue_curr_law.place(relx = button_1_pos_x, 
                                         rely = button_1_pos_y, anchor = "w")

l2=Label(text="Reform", font = "Calibri 12 bold")
l2.place(relx = block_1_title_pos_x, rely = block_2_title_pos_y, anchor = "w")

l3=Label(text="Select Policy Parameter: ", font = "Calibri 10")
l3.place(relx = block_2_entry_1_1_x, 
         rely = block_2_entry_1_1_y-text_entry_gap, anchor = "w")

current_law_policy, policy_options_list = policy_options()
policy_options_list.remove('gst_rate')
block_widget_dict = {}
num_reforms = 1

num_reforms = tk.IntVar()

def Add_Reform(event=None):
    num_reforms.set(num_reforms.get() + 1)

s = ttk.Style()
s.configure('my.TButton', font=('Calibri', 12, 'bold'))
button_add_reform = ttk.Button(text="+", style='my.TButton', command=Add_Reform, width=2)
button_add_reform.place(relx = button_add_reform_x, rely = block_2_entry_1_1_y, anchor = "w")

block_widget_dict[1] = {}
block_widget_dict[1][1] = ttk.Combobox(root, value=policy_options_list)
block_widget_dict[1][1].current(1)
block_widget_dict[1][1].place(relx = block_2_entry_1_1_x, 
                rely = block_2_entry_1_1_y, anchor = "w", width=300)
block_widget_dict[1][1].bind("<<ComboboxSelected>>", show_policy_selection)

l4=Label(text="Year: ", font = "Calibri 10")
l4.place(relx = block_2_entry_1_2_x, 
         rely = block_2_entry_1_1_y-text_entry_gap, anchor = "w")
block_widget_dict[1][2] = Entry(root,width=6)
block_widget_dict[1][2].place(relx = block_2_entry_1_2_x, rely = block_2_entry_1_1_y, anchor = "w")

l5=Label(text="Value: ", font = "Calibri 10")
l5.place(relx = block_2_entry_1_3_x, 
         rely = block_2_entry_1_1_y-text_entry_gap, anchor = "w")
block_widget_dict[1][3] = Entry(root,width=10)
block_widget_dict[1][3].place(relx = block_2_entry_1_3_x, rely = block_2_entry_1_1_y, anchor = "w")



button_genenerate_revenue_policy = ttk.Button(text = "Generate Revenue under Reform", command=apply_policy_change)
button_genenerate_revenue_policy.place(relx = button_1_pos_x, rely = button_2_pos_y, anchor = "w")

l6=Label(text=total_revenue_text1)
#l1.place(x=100,y=30)
l6.place(relx = 0.4, rely = 0.1, anchor = "w")

l7=Label(text=reform_revenue_text1)
#l1.place(x=100,y=30)
l7.place(relx = 0.4, rely = 0.15, anchor = "w")

image = ImageTk.PhotoImage(Image.open("blank.png"))
#image = tk.PhotoImage(file="blank.png")
pic = tk.Label(root, image=image)
pic.place(relx = 0.5, rely = 0.2, anchor = "nw")
pic.image = image

#button(row=6, column=1, sticky = W, pady = (0,25), padx = (0,0))
root.mainloop()