bool DecodeBTLEPacket(int32_t sample, int srate){
	int c;
	//struct timeval tv;
	uint8_t packet_data[500];
    //packet data
	int packet_length;
    //crc of the packet
	uint32_t packet_crc;
    //calculated crc
	uint32_t calced_crc; 
    //packet address 
	uint64_t packet_addr_l;
    //crc map
	uint8_t crc[3];
    //packet header map
	uint8_t packet_header_arr[2];

    //something g_srate is srate(sample rate?)
	g_srate=srate;

	/* extract address */
    // initialize the address
	packet_addr_l=0;
    //While counting up to 4: concatinathe next byte with 
	for (c=0;c<4;c++) packet_addr_l|=((uint64_t)SwapBits(ExtractByte((c+1)*8)))<<(8*c);

	/* extract pdu header */
    // 
	ExtractBytes(5*8, packet_header_arr, 2);

	/* whiten header only so we can extract pdu length */
    //Whiten the header 
	BTLEWhiten(packet_header_arr, 2b, 38);

	if (packet_addr_l==0x8E89BED6){  // Advertisement packet
        //compute the packet length after header dewhitening 
		packet_length=SwapBits(packet_header_arr[1])&0x3F;
	} else {
		packet_length=0;			// TODO: data packets unsupported

	}

	/* extract and whiten pdu+crc */
	ExtractBytes(5*8, packet_data, packet_length+2+3);
	BTLEWhiten(packet_data, packet_length+2+3, 38);

	if (packet_addr_l==0x8E89BED6){  // Advertisement packet
		crc[0]=crc[1]=crc[2]=0x55;
	} else {
		crc[0]=crc[1]=crc[2]=0;		// TODO: data packets unsupported
	}

	/* calculate packet crc */
    //Do CRC calculation 
	calced_crc=BTLECrc(packet_data, packet_length+2, crc);
    //initialize the packet crc
	packet_crc=0;
    // searching three byte crc
	for (c=0;c<3;c++) packet_crc=(packet_crc<<8)|packet_data[packet_length+2+c];

	/* BTLE packet found, dump information */
	if (packet_crc==calced_crc){
		//gettimeofday(&tv, NULL);
		//printf("%ld.%06ld ", (long)tv.tv_sec, tv.tv_usec);
		//printf("BTLE Packet start sample %"PRId32", Threshold:%"PRId32", Address: 0x%08"PRIX64", CRC:0x%06X ",sample,g_threshold,packet_addr_l, packet_crc);
		//printf("length:%d data:",packet_length);
		//for (c=0;c<packet_length+2;c++) printf("%02X ",SwapBits(packet_data[c]));
		//printf("\n");

        //packet metadata
        packetData.clear();
        packetData["Timestamp"] = Pothos::Object(std::chrono::high_resolution_clock::now().time_since_epoch().count());
        packetData["Address"] = Pothos::Object(Poco::format("0x%08x", unsigned(packet_addr_l)));
        packetData["CRC"] = Pothos::Object(Poco::format("0x%06x", unsigned(packet_crc)));
        packetData["SampleIndex"] = Pothos::Object(sample);
        packetData["Threshold"] = Pothos::Object(g_threshold);

        //extracting the device mac address from the packet.

        //extract 6-byte MAC
        std::string mac;
        for (int i = 7; i >= 2; i--)
        {
            mac += Poco::format("%02x:", unsigned(SwapBits(packet_data[i])));
        }
        packetData["MAC"] = Pothos::Object(mac.substr(0, mac.size()-1));

        //extract packet fields
        //very oversimplified for a select number of fields
        uint8_t *data = packet_data + 8;
        int bytesLeft = packet_length+2 - 8;
        while (bytesLeft >= 3)
        {
            size_t len = SwapBits(data[0]);
            if (len >= bytesLeft) break;
            unsigned type = SwapBits(data[1]);
            std::string name;
            bool hasUUID16 = false;
            switch (type)
            {
            case 0x01: name = "Flags"; break;
            case 0x08: name = "Shortened Name"; break;
            case 0x09: name = "Complete Name"; break;
            case 0x16: name = "Service Data"; hasUUID16 = true; break;
            case 0x24: name = "URI"; break;
            case 0xFF: name = "Manufacturer Data"; hasUUID16 = true; break;
            default: name = Poco::format("0x%02x", type); break;
            }

            if (type == 0x01 and len == 2)
            {
                packetData[name] = Pothos::Object(unsigned(SwapBits(data[2])));
            }
            else
            {
                size_t i = 2;
                unsigned uuid16 = 0;
                if (hasUUID16)
                {
                    uuid16 |= unsigned(SwapBits(data[i++])) << 0;
                    uuid16 |= unsigned(SwapBits(data[i++])) << 8;
                    packetData[name + " UUID16"] = Pothos::Object(Poco::format("%02x", unsigned(uuid16)));
                }
                std::string value;
                for (; i < len+1; i++)
                {
                    char ch = SwapBits(data[i]);
                    if (std::isprint(ch)) value.push_back(ch);
                    else value += Poco::format("\\x%02x", unsigned(ch));
                }
                packetData[name] = Pothos::Object(value);
            }
            bytesLeft -= len + 1;
            data += len + 1;
        }

		return true;
	} else return false;
}