=======
# NHL_Playoffs_Tool
A hockey predictions library based on Elo and SRS, similar to the nba_playoff_odds library. 

Main results are the info_table.py script and the prediction_table.py script, as follows:

Pythagorean Win Expectations, Est. SRS, Elo, and Records
Based on Games Played Between: Sep 29 2026 and Oct 27 2026
======  ==============  ==========  ============  =============  =============  ================  =====  =======  ======
Team    Pythag. Wins    Est. SRS    Elo Rating    Away Record    Home Record    Overall Record    Pts    Pts %    Form
======  ==============  ==========  ============  =============  =============  ================  =====  =======  ======
BOS     61              1.49        1568.49       4-2-1          5-1-0          9-3-1             19     0.731    WTWWL
CAR     58              1.253       1789.18       7-1-1          3-1-1          10-2-2            22     0.786    WLWTW
EDM     48              0.871       1529.57       5-0-0          3-2-2          8-2-2             18     0.75     WTTLT
TBL     45              0.83        1778.59       2-3-1          5-0-0          7-3-1             15     0.682    TWWLT
MIN     54              0.751       1587.89       5-3-2          4-0-0          9-3-2             20     0.714    TLWWW
DAL     52              0.676       1738.22       3-1-1          4-3-0          7-4-1             15     0.625    TTTWL
NJD     49              0.575       1471.97       2-2-0          6-2-0          8-4-0             16     0.667    LWWWW
COL     49              0.481       1926.4        2-4-0          4-1-1          6-5-1             13     0.542    WLLWL
TOR     46              0.462       1234.55       3-2-1          4-3-1          7-5-2             16     0.571    WWWWL
VGK     51              0.456       1589.66       3-2-1          6-2-0          9-4-1             19     0.679    WLLTW
NYI     46              0.399       1393.22       2-3-1          4-1-1          6-4-2             14     0.583    WWTLT
ARI     45              0.115       1696.7        4-3-0          4-2-0          8-5-0             16     0.615    LWLTL
OTT     42              0.114       1629.03       3-3-0          5-2-0          8-5-0             16     0.615    LWLWL
NYR     43              -0.006      1456.21       1-5-1          6-1-0          7-6-1             15     0.536    TWLLL
NSH     36              -0.035      1411.01       1-1-3          3-2-2          4-3-5             13     0.542    WLTWT
STL     39              -0.127      1339.24       2-4-0          3-2-1          5-6-1             11     0.458    WLLWW
SEA     44              -0.136      1346.65       4-2-1          3-2-0          7-4-1             15     0.625    TLTWL
MTL     43              -0.154      1624.93       4-1-1          3-2-1          7-3-2             16     0.667    LTTWW
LAK     30              -0.249      1324.07       3-3-2          0-3-0          3-6-2             8      0.364    WTLWL
FLA     43              -0.307      1369.91       5-3-2          2-1-0          7-4-2             16     0.615    WLLWW
SJS     33              -0.459      1336.25       4-3-1          2-3-0          6-6-1             13     0.5      TLTWL
BUF     33              -0.48       1693.85       2-1-3          3-3-0          5-4-3             13     0.542    TTTLT
ANA     35              -0.57       1456.28       4-3-0          1-3-1          5-6-1             11     0.458    LLLWT
DET     36              -0.571      1436.06       2-1-2          3-3-1          5-4-3             13     0.542    TTWLT
PHI     22              -0.695      1550.51       1-4-1          2-3-3          3-7-4             10     0.357    WWWLT
PIT     41              -0.724      1640.6        1-5-1          4-1-0          5-6-1             11     0.458    LLLWT
CGY     27              -0.792      1291.7        1-3-0          4-3-0          5-6-0             10     0.455    LWWWW
CHI     22              -0.927      1235.97       0-4-0          4-4-0          4-8-0             8      0.333    WTLLW
CBJ     32              -1.119      1540.52       1-2-0          4-3-0          5-5-0             10     0.5      TLLTT
VAN     25              -1.477      1016.25       2-5-1          1-5-0          3-10-1            7      0.25     LLLLT
======  ==============  ==========  ============  =============  =============  ================  =====  =======  ======

prediction_table.py - provides odds for top-3 finishes and wildcard playoff entry 




## Attributions
This project incorporates source from the Armadillo C++ Linear Algebra Library for solving the sparse matrices associated with the Simple Rating System.
As such, the attributions of Armadillo will be included in this project in accordance with their wishes:

Copyright 2008-2018 Conrad Sanderson (http://conradsanderson.id.au)

Copyright 2008-2016 National ICT Australia (NICTA)

Copyright 2017-2018 Arroyo Consortium

Copyright 2017-2018 Data61, CSIRO

This product includes software developed by Conrad Sanderson (http://conradsanderson.id.au)

This product includes software developed at National ICT Australia (NICTA)

This product includes software developed at Arroyo Consortium

This product includes software developed at Data61, CSIRO
