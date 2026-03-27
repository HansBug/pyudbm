//This file was generated from (Academic) UPPAAL 4.1.4 (rev. 4724), January 2011

/*
Probability of any node detecting a collision
*/
Pr[time<=160] (<> exists(i:nodeid_t) Node(i).detected>=0) >= 0.1

/*
Probability of any node detecting a collision
*/
Pr[time<=160] (<> exists(i:nodeid_t) Node(i).detected>=0)

/*
Probability of any node detecting a collision on slot 0
*/
Pr[time<=160] (<> exists(i:nodeid_t) Node(i).detected==0)

/*
Probability of any node detecting a collision on slot 1
*/
Pr[time<=160] (<> exists(i:nodeid_t) Node(i).detected==1)

/*
Probability of any node detecting a collision on slot 2
*/
Pr[time<=160] (<> exists(i:nodeid_t) Node(i).detected==2)

/*
Probability of any node detecting a collision on slot 3
*/
Pr[time<=160] (<> exists(i:nodeid_t) Node(i).detected==3)

/*
Probability of any node detecting a collision on slot 4
*/
Pr[time<=160] (<> exists(i:nodeid_t) Node(i).detected==4)

/*
Probability of any node detecting a collision on slot 5
*/
Pr[time<=160] (<> exists(i:nodeid_t) Node(i).detected==5)

/*
Probability of detecting a collision (simpler query)
*/
Pr[time<=160] (<> col_count>0)

/*
Probability distribution of collision counts after 1000 time units
*/
Pr[collisions<=50000] (<> time>=1000)

/*
Probability distribution of energy after 1000 time units
*/
Pr[energy<=50000] (<> time>=1000)
