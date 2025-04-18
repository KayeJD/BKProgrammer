# BK Programmer

## Usage Instructions:

### Running from a CSV file:
1. Locate Your CSV Files: The .csv files are stored in the /lists folder.
2. Start the Application: Run the command: **python controller.py**
3. Select USB Connection: Choose the appropriate USB connection when prompted.
4. Choose Execution Options: When prompted, select option **3** for Execution Options.
5. Run from CSV File: Select option **2** to Run from CSV File.
6. Enter the File Name: **Type the name of the .csv file** you want to use (found in the /lists folder).
7. Finish Running: Once the process is complete, enter **0** to finish.

## Parameters to remember:
.write
- LIST:SLOWrate <0 or 1>
    - 0:High-rate(A/us)     1:Slow-rate(A/ms)
- LIST:RANG <0-max current>
- LIST:SLEW <[step]>, <slew>
    - "slew" refers to the rate of change of current output,
    - essentially how quickly the output can transition from one level to another
    - determined by slowrate
- LIST:COUNt <1 to 65536>
    - number of times a list will execute
    - 65536 = inf
- LIST:STEP <2 to 83>
    - Divides the list to individual sections to differ LEVEL, SLEW, and WIDTH
    - making it to 84 will force it into fixed mode
- LIST:LEV <1 to maxCurrRange>
    - 65536 = inf
- LIST:WIDth <[step]>, <20us to 3600s>
    - length of each step.
    - unit is in seconds
