import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure, plot
import squarify
import pickle
import seaborn as sns
import numpy as np
import datetime


def load_data():
    # read in bank statement
    df = pd.read_csv('/Users/Travis/Documents/Projects/Visualize Monthly Expenses/10_2022.csv') 
    # change cols
    df.columns = ['date','type','check','description','amount'] 
    # remove cols not needed
    df = df[['date','type','description','amount']] 
    # only look at debits, handle credits in future
    df = df[df.type == 'Debit'] 
    # remove $ and convert to float
    df[df.columns[3]] = df[df.columns[3]].replace('[\$,]', '', regex=True).astype(float) 
    # create new column 
    df['category'] = None 
    # grab the month, share as a global var
    month_integer = int(df.date[0].split("/")[0])
    global MONTH
    MONTH = datetime.date(1900, month_integer, 1).strftime('%B')

    return df

def categorize_data(df, load_history = True):
    
    # load known spending to speed up categorization
    with open('/Users/Travis/Documents/Projects/Visualize Monthly Expenses/spending_categories_dict.pickle', 'rb') as handle:
        expenses = pickle.load(handle)

    # print categories
    print(
        'Categories: \n\
        g: groceries\n\
        c: coffee\n\
        cat: cats\n\
        r: restaurant\n\
        e: entertainment\n\
        h: healthcare\n\
        b: bills\n\
        s: security\n\
        i: internet\n\
        p: phone\n\
        hg: home goods\n\
        rent: rent\n\
        t: auto\n\
    ')
    # loop through expense df and assign categories
    for index, row  in df.iterrows():

        # use pickled dict to update values
        if load_history:
            if row[2] in expenses.keys():
                category = expenses[row[2]]

        # if not found, update manually
        else:
            print(f'{row[2]} -- ${row[3]}')
            category = input("Please label your spending or exit: ")
            if category == 'exit':
                break
            while category not in ('g','c','r','e','h','b','s','i','p','hg','t','cat','rent'):
                category = input("Incorrect input. Please label your spending: ")

        df.loc[index,'category']  = category
        
    # save to new expenses
    costs_df = df[df.category.notnull()][['description','category','amount']]
    categories = costs_df[['description', 'category']]
    new_spending = dict(categories.values)
    expenses.update(new_spending)

    # save to csv
    costs_df.to_csv(f'{MONTH}_expenses.csv')

    # update pickle file with new spending categories
    with open('/Users/Travis/Documents/Projects/Visualize Monthly Expenses/spending_categories_dict.pickle', 'wb') as handle:
        pickle.dump(expenses, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return costs_df

def add_checking_expenses(plot_df):
    # rent: 160
    # car ins: 130
    
    plot_df = plot_df.reset_index()
    plot_df["amount"] = pd.to_numeric(plot_df["amount"])
    plot_df.loc[len(plot_df.index)] = ['Rent',1600]
    curr_auto = plot_df[plot_df['category']=='Auto'].amount.values[0]
    plot_df.loc[plot_df[plot_df['category']=='Auto'].index, 'amount']= curr_auto + 130
    plot_df = plot_df.groupby('category').sum()
    return plot_df
  

def treemap_data(cost_df):
    # create dict to map category abbr to full word
    map_dict = {'g':'Groceries','c':'Coffee','r':'Restaurants','e':'Media','h':'Health','b':'Bills','s':'Security','i':'Internet','p':'Phone','hg':'Home','t':'Auto','cat':'Cats'}
    
    cost_df = cost_df.replace({"category": map_dict})
    plot_df = cost_df.groupby('category').sum()

    plot_df = add_checking_expenses(plot_df)

    # save spending by category
    spending_by_cat_df = plot_df.reset_index()
    spending_by_cat_df.to_csv(f'{MONTH}_spending_by_cat.csv')

    # create label values
    perc = [f'{i/plot_df["amount"].sum()*100:5.2f}%' for i in plot_df['amount']]
    cost = [ '%1.0f' % elem for elem in plot_df.amount.values ]
    lbl = [f'{el[0]}:\n{el[1]}:\n${el[2]}' for el in zip(plot_df.index, perc,cost)]

    # create color list
    my_cmap = sns.color_palette("viridis", as_cmap=True)
    mapped_list_5 = [my_cmap(i) for i in np.arange(0, 1, 1/len(lbl))]

    # plot it
    mpl.rcParams['text.color'] = 'white'
    figure(figsize=(28,28), dpi=100)
    squarify.plot(sizes=plot_df['amount'], label=lbl, alpha=.8, linewidth=20, 
        color=mapped_list_5,text_kwargs={'fontsize':27},pad=False,)

    plt.axis('off')
    
    # add text
    title = f'{MONTH} Expenses'
    plt.text(87, 1,                     #sets position to place text using data coordinates
            title,                     #title string
            fontsize = 35, 
            color='black', 
            horizontalalignment='center',#within the text box, aligns horizontally
            verticalalignment='bottom',  #within the text box, aligns towards top? I have no explanation for why syntax seems backward.
            zorder = 20)  
    
    # save image and print to screen
    plt.savefig(f'{MONTH}_expenses.jpg', transparent = False, bbox_inches='tight',pad_inches = 0)
    plt.show()


def main():
    df = load_data()
    cost_df = categorize_data(df, load_history = True)
    treemap_data(cost_df)


if __name__ == "__main__":
    main()