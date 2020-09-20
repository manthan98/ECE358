# Lab 1

All of the code has been separated into methods for each of the questions outlined in the lab manual. To run the main Python code file on terminal use:

`python3 lab1.py`

## M/M/1 Queue

To run the results associated with question 3, call the `q3()` method, and run the Python file. The `q3(T)` method takes a simulation time (T) parameter, which defaults to T = 1000 s if unspecified. The `q3()` method will sweep values of rho across 0.25 and 0.95, and compute the associated E[N] and P_idle values for each value of rho. Two plots will be generated, and saved as en_q3_figure.pdf for E[N] vs rho and pidle_q3_figure.pdf for P_idle vs rho.

To run the results for question 4, call the `q4()` method and run the Python file.

The event generation code (arrival/departure/observer) can be found in the `buildEventsForInfiniteBuffer(...)` method. The DES code for the infinite buffer case can be found in the `infiniteBufferDes(...)` method.
