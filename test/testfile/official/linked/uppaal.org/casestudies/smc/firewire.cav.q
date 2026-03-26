//This file was generated from (Academic) UPPAAL 4.1.4 (rev. 4731), January 2011

/*

*/
E<> ( node1.s == 7 && node2.s == 8 ) 

/*

*/
E<> (!( node1.s == 8 && node2.s == 7 || node1.s == 7 && node2.s == 8) && gc >= 1500)

/*

*/
A<> (( node1.s == 8 && node2.s == 7 || node1.s == 7 && node2.s == 8) || gc < 100)

/*

*/
Pr[time <= 100] (<> node1.s == 7 && node2.s == 8 )

/*

*/
Pr[time <= 150] (<> node1.s == 7 && node2.s == 8 )

/*

*/
Pr[time <= 200] (<> node1.s == 7 && node2.s == 8 )

/*

*/
Pr[time <= 250] (<> node1.s == 7 && node2.s == 8 )

/*

*/
Pr[time <= 300] (<> node1.s == 7 && node2.s == 8 )

/*

*/
Pr[time <= 400] (<> node1.s == 7 && node2.s == 8 )

/*

*/
Pr[time <= 500] (<> node1.s == 7 && node2.s == 8 )

/*

*/
Pr[time <= 600] (<> node1.s == 7 && node2.s == 8 )

/*

*/
Pr[time <= 700] (<> node1.s == 7 && node2.s == 8 )

/*

*/
Pr[time <= 800] (<> node1.s == 7 && node2.s == 8 )

/*

*/
Pr[time <= 900] (<> node1.s == 7 && node2.s == 8 )

/*

*/
Pr[time <= 1000] (<> node1.s == 7 && node2.s == 8 )

/*

*/
Pr[time <= 1000] (<> node1.s == 8 && node2.s == 7 )

/*

*/
Pr[time <= 1500] (<> node1.s == 7 && node2.s == 8 )

/*

*/
Pr[time <= 1500] (<> node1.s == 8 && node2.s == 7 )

/*

*/
Pr[time <= 1500] (<> node1.s == 8 && node2.s == 7 || node1.s == 7 && node2.s == 8)

/*

*/
Pr[time <= 1500] (<> node1.s == 8 && node2.s == 7 ) >= Pr[time <= 1500] (<> node1.s == 7 && node2.s == 8 )

/*

*/
Pr[time <= 1500] (<> node1.s == 7 && node2.s == 8 ) >= Pr[time <= 1500] (<> node1.s == 8 && node2.s == 7 )

/*

*/
Pr[time <= 1500] (<> node1.s == 8 || node1.s == 7 )

/*

*/
Pr[time <= 1500] (<> node2.s == 7 || node2.s == 8 )

/*

*/
Pr[time <= 1500] (<> node1.s == 7 || node1.s == 8 ) >= Pr[time <= 1500] (<> node2.s == 7 || node2.s == 8 )

/*

*/
Pr[time <= 1500] (<> node1.s == 7 )

/*

*/
 Pr[time <= 1500] (<> node2.s == 7 )

/*

*/
Pr[time <= 1500] (<> node2.s == 7 ) >= Pr[time <= 1500] (<> node1.s == 7 )

/*
node 2 is the root and node 1 is the child
*/
A[] not deadlock
