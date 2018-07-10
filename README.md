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


## GNU Radio Project for Scanning Bluetooth LE Advertisement packets 

This project uses [ble dump]() as starting point. 

### Hardware 

USRP B210 and ISM range antenna were used to implement this project. More one the USRP device and potential other Ettus candidate devices, please visit [ettus.com](https://www.ettus.com). The first antenna used for the project was the LP0965 by Ettus research.

### Software 

This is GNU Radio based project and it uses [ble dump]() as starting point.

#### Simulation_utils

#### Parameteric_simulations

### ble dump

### Ble dump Utils 

#### GRC 



