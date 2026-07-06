import math
import numpy as np
from tool._fixedInt import *

a = DeFixedInt(5,2,'S','round','saturate')
b = DeFixedInt(5,2,'S','round','saturate')
c = DeFixedInt(5,4,'S','round','saturate')
sum = DeFixedInt(5,2,'S','round','saturate')

a.value = -1.75
b.value = -0.25
c.value = -0.0625

sum.assign(a + c)

print('float: %f'%a.fValue,' + %f'%c.fValue,' = %f'%sum.fValue)
print('binario: ',bin(a.intvalue),' + ',bin(c.intvalue),' = ',bin(sum.intvalue))

