# BRENDA SOAP API Reference

## Overview
The BRENDA SOAP API provides access to enzyme data.
WSDL: `https://www.brenda-enzymes.org/soap/brenda_zeep.wsdl`

## Common Methods

### Kinetic Data
*   `getKmValue(parameters)`: Retrieve Km values.
*   `getTurnoverNumber(parameters)`: Retrieve kcat values.
*   `getVmax(parameters)`: Retrieve Vmax values.

### Structure & Reaction
*   `getReaction(parameters)`: Get reaction equations.
*   `getSubstrate(parameters)`: Get substrates.
*   `getProduct(parameters)`: Get products.

### Properties
*   `getPhOptimum(parameters)`: Optimal pH.
*   `getTemperatureOptimum(parameters)`: Optimal temperature.
*   `getInhibitor(parameters)`: Inhibitors.
*   `getActivatingCompound(parameters)`: Activators.

## Parameter Format
Parameters are typically passed as a single string delimited by `#` and `*`.
Example: `ecNumber*1.1.1.1#organism*Homo sapiens#...`
