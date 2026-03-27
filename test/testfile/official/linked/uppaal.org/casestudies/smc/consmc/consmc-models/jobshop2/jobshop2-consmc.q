//This file was generated from (Academic) UPPAAL 4.1.16 (5300), August 2013

/*

*/
control: A<> Kim.Done and Jan.Done and time<=80

/*
To get distribution on time to finish reading for both Kim and Jan
*/
Pr[<=80] (<> Kim.Done and Jan.Done)

/*
Total time to finish reading of Jan
*/
E[<=80 ; 200] (max: Jan.t)

/*
Acculumated reading time of Jan
*/
E[<=80 ; 200] (max: Jan.rt)

/*
Acculumated waiting time of Jan
*/
E[<=80 ; 200] (max: Jan.wt)

/*
Total time to finish reading of Kim
*/
E[<=80 ; 200] (max: Kim.t)

/*
Acculumated reading time of Kim
*/
E[<=80 ; 200] (max: Kim.rt)

/*
Acculumated waiting time of Kim
*/
E[<=80 ; 200] (max: Kim.wt)

/*
Kim finishes earlier than Jan
*/
A[] Jan.Done imply Kim.Done

/*
Jan finishes earlier than Kim
*/
A[] Kim.Done imply Jan.Done

/*
Binary search min total time for Kim and Jan to finish
*/
E<> Kim.Done and Jan.Done and time<=45

/*
Binary search min total time for Kim and Jan to finish
*/
E<> Kim.Done and Jan.Done and time<=44
