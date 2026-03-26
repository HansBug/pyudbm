//This file was generated from (Academic) UPPAAL 4.1.16 (5300), August 2013

/*
There is never more than one train crossing the bridge (at
any time instance).
*/
control: A[] forall (i : id_t) forall (j : id_t) Train(i).Cross && Train(j).Cross imply i == j
