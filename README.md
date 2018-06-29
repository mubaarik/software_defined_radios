# software_defined_radios
## Tried so far

- Found the [BLE Dump](https://github.com/drtyhlpr/ble_dump).
- 

## Todo
- [X] Find GMSK demodulator in Python
- [X] Find Write the data from the FIR filter to a file 
- [X] Demodulate the FIR 
- [X] Search for packets
- [X] Create Fake BLE packets and decode them. IF that works, this should also work.
## Todo 2
- [ ] Extract a CMT packet before whitening 
- [ ] fix the convolution operation in the utils to (1) search for the header (2) search for a full whiteted packet.
## Todo 3 
- [ ] Compute pre-demodulation QI signal for the packet.
- [ ] Do the convolution with the QI data, streaming out the dot product.
- [ ] ....



