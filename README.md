# BK Programmer

## Parameters to remember:
.write
    -LIST:SLOWrate <0 or 1>
        - 0:High-rate(A/us)     1:Slow-rate(A/ms)
    -LIST:RANG <p>
        - p:0-max current
    -LIST:SLEW <step>, <p>
        - "slew" refers to the rate of change of current output,
        - essentially how quickly the output can transition from one level to another
        - determined by slowrate
    -LIST:COUNt <1 to 65536>
        - # of times a list will execute
        - 65536 = inf
    -LIST:STEP <2 to 83>
        - Divides the list to individual sections to differ LEVEL, SLEW, and WIDTH
        - making it to 84 will force it into fixed mode
    -LIST:LEV <1 to maxCurrRange>
        - 65536 = inf
    -LIST:WIDth <step>, <20us to 3600s>
        - length of each step.
        - unit is in seconds