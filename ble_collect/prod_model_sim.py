
from util_functions import *
__MAP__ = []


def random_mutation():
	for i in range(10000):
		rand_int = random.randint(0,L-1);
		if TARGET_ARR.bin[rand_int]!=SAMPLE_ARR.bin[rand_int]:
			
			SAMPLE_ARR.invert(rand_int);
			
			break
	for i in range(3):
		rand_int = random.randint(0,L-1);
		SAMPLE_ARR.invert(rand_int)
	return SAMPLE_ARR


def simulate(objective_function):
	i = 0
	try:
		while i<ITERATIONS:
			i+=1;
			
			#print "nochange:", bins==SAMPLE_ARR.bin
			pos_error_poses  = [i for i in range(L) if SAMPLE_ARR.bin[i]!=TARGET_ARR.bin[i]];
			neg_error_poses = [i for i in range(L) if SAMPLE_ARR.bin[i]==TARGET_ARR.bin[i] ]
			# error_poses = []
			# for i in range(L):
			# 	if SAMPLE_ARR.bin[i]!=TARGET_ARR.bin[i]:
			if not 0 in pos_error_poses:
				pos_error_poses=[0]+pos_error_poses
			if not L-1 in pos_error_poses:
				pos_error_poses.append(L-1)
			if not 0 in neg_error_poses:
				neg_error_poses=[0]+neg_error_poses
			if not L-1 in neg_error_poses:
				neg_error_poses.append(L-1)

			pos_islands = [pos_error_poses[i] -pos_error_poses[i-1]  for i in range(len(pos_error_poses)) if i>0];
			neg_islands = [neg_error_poses[i] -neg_error_poses[i-1]  for i in range(len(neg_error_poses)) if i>0];


			pos_map_ = {island:0 for island in pos_islands};
			neg_map_ = {island:0 for island in neg_islands};
			for island in pos_islands:
				pos_map_[island]+=1;
			for island in neg_islands:
				neg_map_[island]+=1;
			prob = {"prob":objective_function(pos_islands,neg_islands),"neg_max": max(neg_islands),"pos_max":max(pos_islands),"pos_islands":pos_map_.items(),"neg_islands": neg_map_.items()};
			#print prob
			D_FRAME.append(prob);
			random_mutation()
			if len(pos_islands)==1:
				break
	except:
		data_frame = pd.DataFrame(D_FRAME);
		data_frame.to_csv(FILENAME);
		print "crashed"
		return
	data_frame = pd.DataFrame(D_FRAME);
	data_frame.to_csv(FILENAME);
def bit_error_rate(objective_function,error_funct,divisions = (1,3,5)):
	percent_list = [i*.1 for i in range(1,6)[::-1]]

	for percent in percent_list:
		print "simulating the "+str(int(percent*100))+"%"
		prob = []
		for i in range(ITERATIONS):
			SAMPLE_ARR = error_funct(BitArray(hex = TARGET),percent,divisions=divisions);
			pos_error_poses  = [i for i in range(L) if SAMPLE_ARR.bin[i]!=TARGET_ARR.bin[i]];
			neg_error_poses = [i for i in range(L) if SAMPLE_ARR.bin[i]==TARGET_ARR.bin[i] ]
			


			if not 0 in pos_error_poses:
				pos_error_poses=[0]+pos_error_poses
			if not L-1 in pos_error_poses:
				pos_error_poses.append(L-1)
			if not 0 in neg_error_poses:
				neg_error_poses=[0]+neg_error_poses
			if not L-1 in neg_error_poses:
				neg_error_poses.append(L-1)


			pos_islands = [pos_error_poses[i] -pos_error_poses[i-1]  for i in range(len(pos_error_poses)) if i>0];
			neg_islands = [neg_error_poses[i] -neg_error_poses[i-1]  for i in range(len(neg_error_poses)) if i>0];

			p=objective_function(pos_islands,neg_islands)
			prob.append(p)
		__MAP__.append((percent,sorted(prob)))










def plot_data_frame(x,y):
	fig = plt.figure(figsize=(30,5))
	ax = fig.add_subplot(111)

	print "x:",x[0:40],"length:",len(x)
	print "y:",y[0:40],"length:",len(x)
	
	ax.plot(x,y);
	plt.show()
def multi_plot(Y,file_name = "filename"):
	fig = plt.figure(figsize=(30,5))
	ax = fig.add_subplot(111)

	ax.clear()
	for y in Y:
		label = str(int(y[0]*100))+"%"
		x = range(len(y[1]));
		y = y[1];
		
		plt.plot(y,x,label=label)
	#print ax.lines
	plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
	#plt.show()
	fig.savefig(file_name)
	fig.show('all')
	fig.clear()
	ax.clear()
	plt.clf()

	
	plt.close(fig)
#multi_plot([(0.5,[12,23,4,4,5,23,23,4,4,2,2]),(0.4,[12,3,5,6,5,3,3,4,4,2,2])])



if __name__=="__main__":
	INTEREST_MAP = ERR_PERCENTS
	for div in INTEREST_MAP:
		bit_error_rate(run_based_model,varying_err_rate, divisions=INTEREST_MAP[div]);
		# print "exiting"
		# x = [d[0] for d in __MAP__]
		# y = [d[1] for d in __MAP__]

		#plot_data_frame(x,y)
		multi_plot(__MAP__,file_name=PATH+div);
		__MAP__ = []








	
