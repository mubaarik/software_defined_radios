import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np 

def coplot(y1,y2):
	x = range(len(y2))
	plt.plot(x,y1,x,y2)
	plt.show()