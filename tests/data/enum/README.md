# Full Grid Enumerations

Enumerations in this directory were generated using [Enumpart](https://github.com/alarm-redist/redist/tree/master/inst/enumpart) from the ALARM Project.

## Reproducing
To reproduce `5x5_all.txt` (all balanced 5x5 → 5 plans with rook adjacency), build `enumpart` and run:
```
./enumpart grid_5x5.dat -k 5 -lower 5 -upper 5 -allsols -comp > 5x5_all.txt
```

