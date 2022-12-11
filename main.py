import streamlit as st
import scipy
import optuna
import pandas as pd

# main functions

def tokens_return(X,Y,dx,comission):
    return (Y*dx/(X+dx))*(1-comission)


def chain_orders(initial_amount=1000,a_dict=a_dict,comission=0.003):
    a_list = []
    amount = initial_amount
    for n in a_dict:
        amount = tokens_return(a_dict[n][0],a_dict[n][1],amount,comission)
        a_list.append(amount)

    amount_difference =  a_list[-1] - initial_amount
    return amount_difference


def optimize_with_scipy(func,a_dict,comission):
    max_x = scipy.optimize.fmin(lambda x: -func(x,a_dict,comission),0)[0]
    amount_difference = func(a_dict,max_x,comission)
    return max_x, amount_difference


def optimize_with_optuna(func,a_dict,comission):
    
    def objective(trial):
        init_amount = trial.suggest_int('init_amount',1,1e+10)
        
        result = func(init_amount,a_dict,comission)
        return result
    
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    # optuna.logging.set_verbosity(optuna.logging.INFO)
    
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=100, timeout=600, n_jobs=-1)
    
    return study.best_params['init_amount'],study.best_value



def golden_section_search(func,xl=0,xr=100000000000,tol=1):
    
    # golden ration plus one
    gr1 = 1 + (1 + 5**0.5)/2
    
    # initial middle point
    xm = xl + (xr - xl)/gr1
    
    # main part
    fl = func(xl)
    fr = func(xr)
    fm = func(xm)
    
    while ((xr - xl) > tol): # while difference between borders is more than tolerance
                             # otherwise return xm
            
        if ((xr - xm) > (xm - xl)): # if the right section is bigger
                                    # make a second inner point 
                                    # as xm + right_section/golden_ratio_plus_one
            
            xm2 = xm + (xr - xm)/gr1
            fm2 = func(xm2)
            
            if fm2 >= fm: # if the value of second inner point is bigger or equal to first
                          # then we move left border point to left middle point (xm)
                          # left middle point (xm) to right middle point (xm2)
                
                xl = xm
                fl = fm
                xm = xm2
                fm = fm2
                 
            else: # otherwise right border point to right middle point
                  # we don't need to move left border and left middle point
                  # as they stay the same
                xr = xm2
                fr = fm2
                
        else: # if left section is bigger
              # second inner point we make as
              # xm - left_section/golden_ratio_plus_one
            xm2 = xm - (xm - xl)/gr1
            fm2 = func(xm2)
            
            if fm2 >= fm: # -||-
                          # we move right border and right middle point closer to center
                xr = xm
                fr = fm
                xm = xm2
                fm = fm2
                 
            else: # otherwise move left border only
                xl = xm2
                fl = fm2
    return xm
                


# streamlit


default_lps = [[3753139396,166740188573],
               [724520588560,766050680304],
               [10457920653,1051487855],
               [1722571966294,2846977754550],
               [22496742244741,4310194783973]]

st.title ("Maximum Value Extraction from Constant Product AMM")

col1, col2 = st.columns(2)
with col1:
    number_of_pairs = st.number_input('Input a number of pairs from 3 to 10',min_value=3,max_value=10,value=5)
with col2:    
    comission = st.number_input('Input comission value from 0 to 0.1',min_value=0.0,max_value=0.1,step=0.001,format="%.3f",value=0.003)


a_dict = {}

for i in range(number_of_pairs):
    a_dict[i] = [0,0]
    
   

for i in a_dict:
    
    try:
        lp_0 = default_lps[i][0]
        lp_1 = default_lps[i][1]
    except:
        lp_0 = 10000
        lp_1 = 10000
        
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write('Pair '+str(i+1))
    with col2:
        a_dict[i][0] = st.number_input('First token LP',min_value=1,max_value=None,key=str(i)+'_0',value=lp_0)
    with col3:
        a_dict[i][1] = st.number_input('Second token LP',min_value=1,max_value=None,key=str(i)+'_1',value=lp_1)




    

        
if st.button('Calculate best initial amount'):
    
    max_x_s, diff_s = optimize_with_scipy(chain_orders,a_dict,comission)
    max_x_o, diff_o = optimize_with_optuna(chain_orders,a_dict,comission)
    
    max_x_gs = golden_section_search(chain_orders)
    diff_o = chain_orders(max_x_gs)
    # st.write([max_x_s,max_x_o])
    
    if (max_x_s > 0) and (max_x_o > 0):
        st.write('Optimization is done with 2 engines: scipy.optimize and optuna')
        st.write('Optuna is probabilistic, so the results may vary')

        result = pd.DataFrame([[max_x_s,max_x_o,max_x_gs],[diff_s,diff_o,diff_o]],
                              columns=['scipy','optuna','golden_section_search'],
                              index=['best_initial_amount','best_difference'])
        result.loc['final_amount'] = result.sum()
        result
    else:
        st.error("Best maximum amount is less or equal to 0. It doesn't work with this LP parameters.")
    
    
with st.expander("Source code"):
    
    st.subheader('Tokens to return in a trade func')
    st.latex(r'\large dy = \frac{Ydx}{X+dx}')
    st.code('''
def tokens_return(X,Y,dx,comission):
    return (Y*dx/(X+dx))*(1-comission)
    ''')

    st.subheader('Chain order func')
    st.write('Actual code for chain orders')
    st.code('''
def chain_orders(a_dict,initial_amount=1000,comission=0.003):
    a_list = []
    amount = initial_amount
    for n in a_dict:
        amount = tokens_return(a_dict[n][0],a_dict[n][1],amount,comission)
        a_list.append(amount)

    amount_difference =  a_list[-1] - initial_amount
    return amount_difference
    ''')
    
    st.write('Example code for 5 pairs chain order. Not used.')
    st.code('''
def chain_orders_for_5_pairs(lp_list,amount_to_buy,comission):

    # first step
    # Sell A, buy B
    B = tokens_return(*lp_list[0],amount_to_buy,comission)

    # second step
    # Sell B, buy C
    C = tokens_return(*lp_list[1],B,comission)

    # third step
    # Sell C, buy D
    D = tokens_return(*lp_list[2],C,comission)

    # fourth
    # D -> E
    E = tokens_return(*lp_list[3],D,comission)

    # last
    # E -> A
    A_result = tokens_return(*lp_list[4],E,comission)


    return A_result - amount_to_buy
    
lp_list = [[3753139396,166740188573],
           [724520588560,766050680304],
           [10457920653,1051487855],
           [1722571966294,2846977754550],
           [22496742244741,4310194783973]]

chain_orders_for_5_pairs(lp_list,1000,COMISSION)
    ''')
    

    st.subheader('Optimization with scipy.optimize')
    st.code('''
def optimize_with_scipy(func,a_dict,comission):
    max_x = scipy.optimize.fmin(lambda x: -func(a_dict,x,comission),0)[0]
    amount_difference = func(a_dict,max_x,comission)
    return max_x, amount_difference
    ''')
        
    st.subheader('Optimization with optuna')
    st.code('''
def optimize_with_optuna(func,a_dict,comission):

    def objective(trial):
        init_amount = trial.suggest_int('init_amount',1,1e+10)

        result = func(a_dict,init_amount,comission)
        return result

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    # optuna.logging.set_verbosity(optuna.logging.INFO)

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=100, timeout=600, n_jobs=-1)

    return study.best_params['init_amount'],study.best_value
    ''')
    
if st.button('Success'):
    st.balloons()
    
    
st.markdown('''
Made by Alexander Evdokimov  
[Telegram](https://t.me/snakerzr)  
[This Github repo](https://github.com/snakerzr/Max_value_extraction_from_CPAMM)  
''')
