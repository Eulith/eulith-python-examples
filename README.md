# Overview
This repo contains short scripts that do basic things via Eulith. 

These scripts are designed to give you a brief introduction to our services. We're always available to help
you onboard & answer questions.

Please note the examples contained in this repo do NOT constitute a comprehensive summary of our services. These
are a few of the most simple possible building blocks we've chosen to demonstrate.

You can see:

* A basic swap
* Some ERC20 handling
* How to use a KMS wallet (recommended for production systematic signing)
* Send transactions & interact with your toolkit contract
* Get quotes for Uniswap interactions
* Making an atomic transaction
* Getting live market data

# Run
## 1. `./setup.sh <EULITH_TOKEN>`
## 2. `./run.sh`

You can run a variety of Eulith examples from this script. Here are the options:
1. -e   |  ERC20 handling
2. -k   |  KMS
3. -s   |  Swap For Armor
4. -w   |  Swap for Wallet
5. -t <TO_ADDRESS>  |  Simple Transfer
6. -c               |  Transfer from toolkit contract
7. -u | Uniswap quoting (float price & sqrt limit price)
8. -a   |  Atomic Transaction
9. -m   |  Live Market Data
10. -p | Uniswap price streaming
11. -x | Open a short position on WETH with USDC collateral
12. -d | Demonstrate DefiArmor (WARNING: this is expensive)


If you would like to examine the code for the examples, have a look at the files in the examples folder.

## Examples
`./run.sh -e`

`./run.sh -t 0xB6c0d1AC638e1Fe06dBBA649a727C8Ebd306A6c8`

`./run.sh -k`

`./run.sh -s`

`./run.sh -c`

`./run.sh -u`

`./run.sh -a`

`./run.sh -m`

`./run.sh -w`
