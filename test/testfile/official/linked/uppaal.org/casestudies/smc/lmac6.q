//This file was generated from (Academic) UPPAAL 4.1.4 (rev. 4724), January 2011

/*
The most basic property is freedom from deadlocks

*/
A[] not deadlock

/*
Nodes should be synchronised halfway the duration of a slot, since at this time they will send and receive information. Prove for each pair (i, j) of first-order neighbours

*/
A[] forall(i: nodeid_t) forall(j: nodeid_t) (Node(i).t==1 imply Node(j).t==1)

/*
Eventually node 0 and 1 allocate different slots? Answer: yes
*/
A<> (slot_no[0]!=slot_no[1] and slot_no[0]>=0 and slot_no[1]>=0)

/*
Eventually node 0 and 2 allocate different slots? Answer: yes
*/
A<> (slot_no[0]!=slot_no[2] and slot_no[0]>=0 and slot_no[2]>=0)

/*
Eventually node 0 and 3 allocate different slots? Answer: NO (strange)
*/
A<> (slot_no[0]!=slot_no[3] and slot_no[0]>=0 and slot_no[3]>=0)

/*
Eventually node 1 and 2 allocate different slots? Answer: NO (strange)
*/
A<> (slot_no[1]!=slot_no[2] and slot_no[1]>=0 and slot_no[2]>=0)

/*
Eventually node 1 and 3 allocate different slots? Answer: NO (strange)
*/
A<> (slot_no[1]!=slot_no[3] and slot_no[1]>=0 and slot_no[3]>=0)

/*
Eventually node 2 and 3 allocate different slots? Answer: NO (maybe OK)
*/
A<> (slot_no[2]!=slot_no[3] and slot_no[2]>=0 and slot_no[3]>=0)

/*
Eventually all nodes allocate different slots? Answer: NO (strange)
*/
A<> forall(i: nodeid_t) forall(j: nodeid_t) (i==j || (slot_no[i]>=0 && slot_no[j]>=0 && slot_no[i]!=slot_no[j]))

/*

*/
sup: Node(0).detected, Node(1).detected, Node(2).detected, Node(3).detected

/*

*/
E<> exists(i:nodeid_t) Node(i).detected>=0

/*

*/
Pr[time<=100] (<> exists(i:nodeid_t) Node(i).detected>=0)
