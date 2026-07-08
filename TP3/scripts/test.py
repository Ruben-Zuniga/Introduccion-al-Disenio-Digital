import math
import numpy as np
from tool._fixedInt import *

# a = DeFixedInt(5,2,'S','round','saturate')
# b = DeFixedInt(5,2,'S','round','saturate')
# c = DeFixedInt(5,4,'S','round','saturate')
# sum = DeFixedInt(5,2,'S','round','saturate')

# a.value = -1.75
# b.value = -0.25
# c.value = -0.0625

# sum.assign(a + c)

# print('float: %f'%a.fValue,' + %f'%c.fValue,' = %f'%sum.fValue)
# print('binario: ',bin(a.intvalue),' + ',bin(c.intvalue),' = ',bin(sum.intvalue))

# print(sum)

# s64_range = np.arange(-2.0, 1.9375, 0.0625)
# float_range = np.arange(-2.0, 2.0, 0.0625) # S(6,4)
# float_range = np.arange(-1.0, 1.0, 0.007812) # S(8,7)
float_range = np.arange(-1.0, 1.0, 0.25) # S(3,2)

float_func = np.sin(t/T)
fixed_range = arrayFixedInt(3, 2, float_range, 'S', 'trunc', 'saturate')
fixed_range_fvalue = np.array([val.fValue for val in fixed_range])
fixed_func = arrayFixedInt(3, 2, float_func, 'S', 'trunc', 'saturate')
fixed_func_fvalue = np.array([val.fValue for val in fixed_func])

print(fixed_range[0].showValueRange())