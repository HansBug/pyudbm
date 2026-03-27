//This file was generated from (Academic) UPPAAL 4.1.4 (rev. 4724), January 2011

/*
Collision count comparison of two networks.
*/
Pr[time<=70] (<> col_count[1]>0) >= Pr[time<=70] (<> col_count[2]>0)

/*
Collision count comparison with reversed sides
*/
Pr[time<=70] (<> col_count[2]>0) >= Pr[time<=70] (<> col_count[1]>0)

/*

*/
Pr[time<=70] (<> col_count[1]>0)

/*

*/
Pr[time<=70] (<> col_count[2]>0)

/*

*/
Pr[energy1<=10000] (<> time>=1000) >= Pr[energy2<=10000] (<> time>=1000)

/*
Energy comparison with reversed sides
*/
Pr[energy2<=10000] (<> time>=1000) >= Pr[energy1<=10000] (<> time>=1000)

/*
Energy estimation for the first network
*/
Pr[energy1<=10000] (<> time>=1000)

/*
Energy estimation for the second network
*/
Pr[energy2<=10000] (<> time>=1000)
