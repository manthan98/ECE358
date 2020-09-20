{\rtf1\ansi\ansicpg1252\cocoartf2513
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww10800\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # Lab 1\
\
All of the code has been separated into methods for each of the questions outlined in the lab manual. To run the main Python code file on terminal use:\
\
`python3 lab1.py`\
\
## M/M/1 Queue\
\
To run the results associated with question 3, call the `q3()` method, and run the Python file. The `q3(T)` method takes a simulation time (T) parameter, which defaults to T = 1000 s if unspecified. The `q3()` method will sweep values of rho across 0.25 and 0.95, and compute the associated the E[N] and P_idle values for each value of rho. Two plots will be generated, and saved as en_q3_figure.pdf for E[N] vs rho and pidle_q3_figure.pdf for P_idle vs rho.\
\
To run the results for question 4, call the `q4()` method and run the Python file.\
\
The event generation code (arrival/departure/observer) can be found in the `buildEventsForInfiniteBuffer(\'85)` method. The DES code for the infinite buffer case can be found in the `infiniteBufferDes(\'85)` method.}