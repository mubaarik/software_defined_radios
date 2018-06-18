//Inputs
// 1. data: data to be whiten
// 2. length of the data to be whiten
// 3. The source channel
//Operation 
// 1. compute the lfsr
//Output
//
void BTLEWhiten(uint8_t* data, uint8_t len, uint8_t chan){

	uint8_t  i;
	uint8_t lfsr = SwapBits(chan) | 2;
	while(len--){
		// 
		for(i = 0x80; i; i >>= 1){

			if(lfsr & 0x80){

				lfsr ^= 0x11;
				(*data) ^= i;
			}
			lfsr <<= 1;
		}
		data++;
	}
}

