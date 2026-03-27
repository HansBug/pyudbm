//This file was generated from (Academic) UPPAAL 4.1.16 (5300), August 2013

/*
Min time for both Kim and Jan finish reading (binary search method)
*/
E<> Kim.Done and Jan.Done and time<=44

/*
Min time for both Kim and Jan finish reading (binary search method)
*/
E<> Kim.Done and Jan.Done and time<=45

/*
Jan finishes reading before Kim
*/
A[] Kim.Done imply Jan.Done

/*
Kim finishes reading before Jan
*/
A[] Jan.Done imply Kim.Done

/*
Reachability
*/
A<> Kim.Done and Jan.Done and time<=80
