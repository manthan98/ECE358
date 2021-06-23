# Lab 2

All of the code has been separated into methods for each of the questions outlined in the lab manual. To run the main Python code file on terminal use:

`python3 lab2.py`

You must call the specific method under the comment `# Call method here` in the `lab2.py` file to run a specific part of the lab. Nothing will be run by default.

## Persistent CSMA/CD

To run the results associated with question 1, call the `q1()` method, and run the Python file. The `q1()` method will sweep through all values of N for all values of A with the pre-defined constants as defined in the lab manual. The average time it takes to run `q1()` with default T = 1000 s for each simulation is approximately 27 minutes. At the end of the simulation, two plots will be generated and saved as `persistent_csma_cd_eff.png` and `persistent_csma_cd_tput.png`, for efficiency and throughput, respectively.

The code to populate a LAN with nodes can be found in the `populate_nodes(...)` method. The persistent CSMA/CD simulation code can be found in the `persistent_csma_cd(...)` method.

## Non-persistent CSMA/CD

To run the results associated with question 2, call the `q2()` method, and run the Python file. The `q2()` method will sweep through all values of N for all values of A with the pre-defined constants as defined in the lab manual. The average time it takes to run `q2()` with default T = 1000 s for each simulation is approximately 10 minutes. At the end of the simulation, two plots will be generated and saved as `non_persistent_csma_cd_eff.png` and `non_persistent_csma_cd_tput.png`, for efficiency and throughput, respectively.

The code to populate a LAN with nodes can be found in the `populate_nodes(...)` method. The non-persistent CSMA/CD simulation code can be found in the `non_persistent_csma_cd(...)` method.
