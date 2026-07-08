**Daily Set-up — formal representation of each query and its resulting count**

For each transaction type $k$, comparing yesterday's snapshot $Y_k$ with today's
snapshot $T_k$:

| Query (set operation) | Result (count) |
|:--|:--:|
| $\lvert Y_k \cap T_k \rvert$ | $a_k$ |
| $\lvert Y_k \setminus T_k \rvert$ | $b_k$ |
| $\lvert T_k \setminus Y_k \rvert$ | $c_k$ |
| $a_k + b_k + c_k$ | $n_k$ |

Where:

- $Y_k$ — the set of transaction URIs of type $k$ in **yesterday's** snapshot.
- $T_k$ — the set of transaction URIs of type $k$ in **today's** snapshot.
- $\cap$ — *intersection*: members present in **both** sets.
- $\setminus$ — *set difference*: members in the left set but **not** the right.
- $\lvert\,\cdot\,\rvert$ — *cardinality*: the count of members in a set.
- $a_k$ — retained (in both $Y_k$ and $T_k$).
- $b_k$ — removed (in $Y_k$ only).
- $c_k$ — added (in $T_k$ only).
- $n_k$ — total unique transactions of type $k$ across both days.
