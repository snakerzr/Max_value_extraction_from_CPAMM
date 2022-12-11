def tokens_return(X,Y,dx,comission):
    return (Y*dx/(X+dx))*(1-comission)


def chain_orders(a_dict,initial_amount=1000,comission=0.003):
    a_list = []
    amount = initial_amount
    for n in a_dict:
        amount = tokens_return(a_dict[n][0],a_dict[n][1],amount,comission)
        a_list.append(amount)

    amount_difference =  a_list[-1] - initial_amount
    return amount_difference



def golden_section_search(func,a_dict,xl=0,xr=100000000000,tol=0.01):
    
    # golden ration plus one
    gr1 = 1 + (1 + 5**0.5)/2
    
    # initial middle point
    xm = xl + (xr - xl)/gr1
    
    # main part
    fl = func(a_dict,xl)
    fr = func(a_dict,xr)
    fm = func(a_dict,xm)
    
    while ((xr - xl) > tol): # while difference between borders is more than tolerance
                             # otherwise return xm
            
        if ((xr - xm) > (xm - xl)): # if the right section is bigger
                                    # make a second inner point 
                                    # as xm + right_section/golden_ratio_plus_one
            
            xm2 = xm + (xr - xm)/gr1
            fm2 = func(a_dict,xm2)
            
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
            fm2 = func(a_dict,xm2)
            
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



if __name__ == '__main__':
    
    default_lps = [[3753139396,166740188573],
               [724520588560,766050680304],
               [10457920653,1051487855],
               [1722571966294,2846977754550],
               [22496742244741,4310194783973]]
    
    a_dict = {}

    for i in range(5):
        a_dict[i] = default_lps[i]


    max_x_gs = golden_section_search(chain_orders,a_dict)
    diff_gs = chain_orders(a_dict,max_x_gs)
    
    if max_x_gs > 0:
        print(f'Best initial amount: {max_x_gs}')
        print(f'Best difference: {diff_gs}')
        print(f'Best final amount: {max_x_gs + diff_gs}')
    else:
        print("Best maximum amount is less or equal to 0. It doesn't work with this LP parameters.")    