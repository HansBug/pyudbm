//This file was generated from (Academic) UPPAAL 4.1.16 (5300), August 2013

/*
control objective - safety problem
*/
control: A[] forall (i : id_t) forall (j : id_t) Train(i).Cross && Train(j).Cross imply i == j

/*
Throughput at Cross
*/
E[<=100 ; 2000] (max: ncr)

/*
expected engine consumptionn of a Train
*/
E[<=100 ; 2000] (max: Train(0).eng)

/*
expected engine consumptionn of a Train
*/
E[<=100 ; 2000] (max: Train(1).eng)

/*
Train(1) can approach Start when Train(0) is still crossing
*/
E<> Train(0).Cross && Train(1).Start

/*
Is the path Appr--Cross taken?
*/
E<> ap2cr == true
