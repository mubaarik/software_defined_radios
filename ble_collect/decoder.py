from proto import *
#####
disable_dewhitening = False
#####
__map__=[]
def generate_buffer(data):
	l = len(data)-(len(data)%2)*1
	
	return data[0:l].decode('hex')
def compute_hamnming_distance(data,target="2cb84c", thresh=2):
	start = 0
	end = len(target)
	n = len(data);
	while end<=n:
		binary1 = bin(int(target,16)^int(data[start:end],16))
		
		binary = binary1.count('0')
		if binary>=len(target)*4-thresh or binary1=='0b0':
			print "mac_address:",data
			__map__.append(data)
		start+=1
		end+=1

def __buffer__(data):
	current_ble_chan = 38
	pos = 0
	try:
		_buffer = generate_buffer(data);
	except:
		return

	pos += BLE_PREAMBLE_LEN

	# Check enough data is available for parsing the BLE Access Address
	if len(_buffer[pos:]) < (BLE_ADDR_LEN + BLE_PDU_HDR_LEN):
		print "Not enough data";
		return "Not enough data"

	# Extract BLE Access Address
	ble_access_address = unpack('I', _buffer[pos:pos + BLE_ADDR_LEN])[0]



	pos += BLE_ADDR_LEN

	# Dewhitening received BLE Header
	if disable_dewhitening == False:
		ble_header = dewhitening(_buffer[pos:pos + BLE_PDU_HDR_LEN], current_ble_chan)
	else:
		ble_header = _buffer[pos:pos + BLE_PDU_HDR_LEN]


	# Check BLE PDU type
	ble_pdu_type = ble_header[0] & 0x0f

	if ble_pdu_type not in BLE_PDU_TYPE.values():
		pass
		#print "Header is not recognized"
		#return "Header is not recognized"

	# Extract BLE Length
	ble_len = ble_header[1] & 0x1f


	# Dewhitening BLE packet
	if disable_dewhitening == False:
		ble_data = dewhitening(_buffer[pos:pos + BLE_PDU_HDR_LEN + BLE_CRC_LEN + ble_len], current_ble_chan)
	else:
		ble_data = _buffer[pos:pos + BLE_PDU_HDR_LEN + BLE_CRC_LEN + ble_len]

	
	import binascii
	mac_address = binascii.hexlify(bytearray(ble_data))
	if "2c7741"==mac_address[0:6]:
		print "finding matches: ",mac_address

	if "2cb84c" in mac_address:
	 	print "mac address:", mac_address



	
	compute_hamnming_distance(mac_address, target="2cb84c",thresh=3)
#S__buffer__("aad6be898e96d8b4a7a53fcfe299a429d18402cd6ce53e932062163807444c8c32329d")
