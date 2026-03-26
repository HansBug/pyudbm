//This file was generated from (Academic) UPPAAL 4.1.4 (rev. 4724), January 2011

/*

*/
Pr[time<=5000](<> receiver1.Reply)

/*

*/
Pr[time<=10000](<> receiver1.Reply)

/*

*/
Pr[time<=15000](<> receiver1.Reply)

/*

*/
Pr[time<=20000](<> receiver1.Reply)

/*

*/
Pr[time<=25000](<> receiver1.Reply)

/*

*/
Pr[time<=30000](<> receiver1.Reply)

/*

*/
Pr[time<=35000](<> receiver1.Reply)

/*

*/
Pr[time<=40000](<> receiver1.Reply)

/*

*/
Pr[time<=45000](<> receiver1.Reply)

/*

*/
Pr[time<=50000](<> receiver1.Reply)

/*

*/
Pr[time<=55000](<> receiver1.Reply)

/*

*/
Pr[time<=60000](<> receiver1.Reply)

/*

*/
Pr[time<=65000](<> receiver1.Reply)

/*

*/
Pr[time<=70000](<> receiver1.Reply)

/*

*/
Pr[energy<=1000] (<> time>=10000)

/*

*/
E[time<=10000; 10000] (max: receiver1.energy)

/*

*/
Pr[step<=1000](<>rep ==mrep)

/*

*/
Pr[step<=1000](<>rep ==mrep)

/*

*/
Pr[time<=14012] (<> rep >=12)

/*

*/
E<>rep >=2

/*

*/
Pr[step <= 50] (<> (freq == f + o * 16 && s== 1))

/*

*/
E<>rep >= 2

/*

*/
E<> receiver1.wait

/*

*/
E<> receiver1.Reply

/*

*/
E<> receiver1.scan
