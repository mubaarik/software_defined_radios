#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <bitset>
//#include <gnuradio/thread/thread.h>

using namespace std;
string TEMPALATE[] = {"d3","73","80","31","83","ab","10","95","3e","48","90","39","dd","3b","36","23","6a","29","f0","b0","c6","f8","ba","00","b9"};
string TEMPALATE_BIN[] = {"11010011","01110011","10000000","00110001","10000011","10101011","00010000","10010101","00111110","01001000","10010000",
"00111001","11011101","00111011","00110110","00100011","01101010","00101001","11110000","10110000","11000110","11111000","10111010","00000000","10111001"};
string TEMPALATE_STR = "11010011011100111000000000110001100000111010101100010000100101010011111001001000100100000011100111011101001110110011011000100011011010100010100111110000101100001100011011111000101110100000000010111001";
int LEN = 25;
double THRESHOLD = 0.7;

double ISLAND_GAIN = 1.5;

double compute_prob(string s)
{
	int islands = 0;
	int size = 0;
	int polar = 1;
	int i = 0;
	while(i<TEMPALATE_STR.size())
	{
		if (polar==1)
		{
			if (s[i]==TEMPALATE_STR[i])
			{
				size++;
			}
			else
			{
				polar=-1;
				islands+=1;
				size=1;
			}

		}
		else
		{
			if(s[i]==TEMPALATE_STR[i])
			{
				polar=1;
				islands+=1;
				size=1;
			}
			else
			{
				size++;
			}
		}
	i++;

	}
	
	return (LEN*8.0-(double)islands)/(LEN*8.0);
}

int main(){
	//initialize the array
	vector<string> packet;
	stringstream stream;
	string bits = "";


	string line;
	ifstream file_to_read("/Users/mmohamoud/software_defined_radios/ble_collect/demoded_data_lewis_test");
	
	if(file_to_read.is_open()){
		while(file_to_read)
		{
			int integer = file_to_read.get();

			bitset<8> b(integer);
			



			if (bits.size()<(LEN-1)*8){
				bits+=b.to_string();
			
			}
			else{
				bits+=b.to_string();
				
				double prob = compute_prob(bits);
				
				
				
				
				if(prob>THRESHOLD){

					cout<<"bits:"<<bits<<"prob:"<<prob<<endl;
					
					

				}
				bits=bits.substr(8,-1);

			}

			
			
			
						

		}
		file_to_read.close();

	}
	else cout << "Unable to open file";
	return 0;
	
}
