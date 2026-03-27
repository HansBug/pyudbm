//This file was generated from (Academic) UPPAAL 4.1.16 (5300), August 2013

/*
Is the path Appr--Cross taken?
*/
E<> ap2cr == true

/*
Strategy allows two trains approach Cross concurrently
*/
E<> Train(0).Cross && Train(1).Start or Train(1).Cross && Train(0).Start

/*
Mutual exclusive at Cross
*/
A[] forall (i : id_t) forall (j : id_t) Train(i).Cross && Train(j).Cross imply i == j
