//This file was generated from (Academic) UPPAAL 4.1.16 (5300), August 2013

/*
expected total time for Jan to finish reading
*/
E[time<=80 ; 200] (max: Jan.t)

/*
expected reading time for Jan
*/
E[time<=80 ; 200] (max: Jan.rt)

/*
expected idea time for Jan
*/
E[time<=80 ; 200] (max: Jan.wt)

/*
expected total time for Kim to finish reading
*/
E[time<=80 ; 200] (max: Kim.t)

/*
expected reading time for Kim
*/
E[time<=80 ; 200] (max: Kim.rt)

/*
expected idle time for Kim
*/
E[time<=80 ; 200] (max: Kim.wt)

/*
Probability distribution of time
*/
Pr[time<=80](<> Kim.Done and Jan.Done)
