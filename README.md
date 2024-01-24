# decawave-1001-rjg
## Introduction
This is a device driver enable use of a Decawave 1001 UWB positioning module over UART.

The Decawave is a low cost UWB positioning module. A group of at least 4 modules forms a mesh network that can locate a fifth, mobile module with an accuracy of around +-0.2 meters. For more information and datasheets see [Decawave's website](https://www.decawave.com/product/dwm1001-development-board/).

The UART API is supported over either GPIO pins for a raspberry pi, or over USB.

The DWM1001 is available as a development board about the size of a credit card.

## Driver Features
* Connects over UART
* Optionally enables high priority thread scheduling

## Limitations
* Requires python 3.7

## Examples
Examples are available on [Github](https://github.com/gandres42/decawave-1001-rjg/tree/master/examples).
