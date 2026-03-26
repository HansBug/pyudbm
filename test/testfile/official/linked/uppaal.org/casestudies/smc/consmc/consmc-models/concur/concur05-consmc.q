//This file was generated from (Academic) UPPAAL 4.1.4 (rev. 5535), March 2014

/*
Winning in goal
*/
control: A<> Main.goal

/*
Probability to reach goal within 30
*/
Pr[<=30](<>Main.goal)

/*
Total number of transition steps
*/
E[<=30;200] (max: Main.s)

/*
Engine consumption
*/
E[<=30;200] (max: Main.e)

/*
Control objective
*/
A<> Main.goal

/*
Total time to reach goal
*/
A<> Main.goal and time<=20
