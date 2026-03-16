## Clocks, DBMs and States in Timed Systems

## Johan Bengtsson

A Dissertation submitted for the Degree of Doctor of Philosophy Department of Information Technology Uppsala University

June 2002

--- end of page.page_number=1 ---

Dissertation for the Degree of Doctor of Philosophy in Computer science with specialization in Real Time Systems presented at Uppsala University in 2002.

## ABSTRACT

Bengtsson, J. 2002: Clocks, DBMs and States in Timed Systems. Acta Universitatis Upsaliensis _Uppsala Dissertations from the Faculty of Science and Technology_ 39. 143 pp. Uppsala. ISBN 91-554-5350-3

Today, computers are used to control various technical systems in our society. In many cases, time plays a crucial role in the operation of computers embedded in such systems. This thesis is about techniques and tools for the analysis of timing behaviours of computer systems. Its main contributions are in the development and implementation of UPPAAL, a tool designed to automate the analysis process of systems modelled as timed automata.

As the first contribution, we present a software package for timing constraints represented as Difference Bound Matrices. We describe in details, all data-structures and operations for DBMs needed in state-space exploration of timed automata, as well as techniques for efficient implementation. In particular, we have developed two normalisation algorithms to guarantee termination of reachability analysis for timed automata containing constraints on clock differences, that transform DBMs according to not only maximal constants of clocks as in algorithms published in the literature, but also difference constraints appearing in the automata. The second contribution of this thesis is a collection of low level optimisations on the internal data-structures and algorithms of UPPAAL to minimise memory and time consumption. We present compression techniques to allow the state-space of a system to be efficiently stored and manipulated in main memory. We also study super-trace and hash-compaction methods for timed automata to deal with system-models for which the size of available memory is too small to store the explored state-space. Our experiments show that these techniques have greatly improved the performance of UPPAAL. The third contribution is in partial-order reduction techniques for timed-systems. A major problem in automatic verification is the large number of redundant states and transitions introduced by modelling concurrent events as interleaved transitions. We propose a notion of committed locations for timed automata. Committed locations are annotations that can be used for not only modelling of intermediate states within atomic transitions, but also guiding the model checker to ignore unnecessary interleavings in state-space exploration. The notion of committed locations has been generalised to give a local-time semantics for networks of timed automata, which allows for the application of existing partial order reduction techniques to timed systems.

_Johan Bengtsson, Department of Information Technology, Uppsala University, Box 337, SE-751 05 Uppsala, Sweden._

c Johan Bengtsson 2002

ISSN 1104-2516 ISBN 91-554-5350-3 Printed in Sweden by Elanders Gotab, Stockholm 2002 Distributor: Uppsala University Library, Box 510, SE-751 20 Uppsala, Sweden

--- end of page.page_number=2 ---

_Till Erika och Simon_

--- end of page.page_number=3 ---

--- end of page.page_number=4 ---

## **Acknowledgements**

First of all I want to thank my supervisor, Wang Yi. Without his guiding and support this thesis would never have been completed. I have learnt a lot during the years we have been working together and I hope that someday I will be as good a reasearcher as he is. I would like to thank all current and former members of the UPPAAL group here in Uppsala, _i.e._ Tobias Amnell, Alexande David, Elena Fersman, Fredrik Larsson, Leonid Mokrushin, Paul Pettersson, and Justin Pearson, for the stimulating environment and all nice moments both in and outside the department. Specially I would like to thank Fredrik and Paul who were around from the very beginning of the UPPAAL-project. I would also like to thank Kim G. Larsen, Gerd Behrmann, and the rest of the UPPAAL group in Aalborg for fruitful collaboration over the years. Without their participation UPPAAL would not have been what it is today. I am also grateful to my coauthors, _i.e._ Pedro D’Argenio, Ansgar Fehnker, David Griffioen, Bengt Johnsson and Johan Lilius, for fruitful discussions. It has been fun working together with you.

I would like to thank everyone at DoCS for making the department such an enjoyable environment. In particular I would like to thank Björn Victor and Anders Berglund for their support.

To my wife Erika, I give my love and my deepest thanks. Without her by my side I would never have reached this point. Finally, I want to thank my son Simon, my pride and joy, and my best source of inspiration.

This work has been partially supported by the Swedish Board for Technical Development (NUTEK), the Swedish Technical Research Council (TFR), and EC via the AIT-WOODDES project.

--- end of page.page_number=5 ---

--- end of page.page_number=6 ---

This thesis includes, summarises and discusses mainly the results presented in five research papers written between 1996 and 2002. These papers are listed as follows:

- **Paper A:** Johan Bengtsson. DBM: Structures, Operations and Implementation. Submitted for publication.

- **Paper B:** Johan Bengtsson and Wang Yi. Reachability Analysis of Timed Automata Containing Constraints on Clock Differences. Submitted for publication.

- **Paper C:** Johan Bengtsson and Wang Yi. Reducing Memory Usage in Symbolic State-Space Exploration for Timed Systems. Technical Report, 2001009, Department of Information Technology, Uppsala University, 2001.

- **Paper D:** Johan Bengtsson, Bengt Jonsson, Johan Lilius and Wang Yi. Partial Order Reductions for Timed Systems. In _Proceedings, Ninth International Conference on Concurrency Theory_ , volume 1466 of Lecture Notes in Computer Science, Springer Verlag, 1998.

- **Paper E:** Johan Bengtsson, W. O. David Griffioen, Kåre J. Kristoffersen, Kim G. Larsen, Fredrik Larsson, Paul Pettersson and Wang Yi. Automated Verification of an Audio-Control Protocol using UPPAAL. Accepted for publication in _Journal on Logic and Algebraic Programming_ .

## **Comments on My Participation**

- **Paper A:** I implemented the major part of the DBM package in UPPAAL, and wrote the report.

- **Paper B:** I participated in discussions, designed and implemented the algorithms. I wrote a large part of the paper.

- **Paper C:** I participated in discussions, designed and implemented the optimisation techniques. I wrote the paper.

- **Paper D:** I participated in discussions and wrote part of the paper. I made a prototype implementation which is not described in this paper.

- **Paper E:** I participated in discussions and implemented committed locations in UPPAAL. I have also made minor revisions to the semantics for committed location.

--- end of page.page_number=7 ---

Apart from the papers listed above, I have also participated in the following work:


![](content_assets/paper.pdf-0008-01.png)



![](content_assets/paper.pdf-0008-02.png)



![](content_assets/paper.pdf-0008-03.png)



![](content_assets/paper.pdf-0008-04.png)


- Tobias Amnell, Gerd Behrmann, Johan Bengtsson, Pedro R. D’Argenio, Alexandre David, Ansgar Fehnker, Thomas Hune, Bertrand Jeannet, Kim G. Larsen, M. Oliver Möller, Paul Pettersson, Carsten Weise, and Wang Yi. UPPAAL - Now, Next, and Future. In _Proceedings of Modelling and Verification of Parallel Processes_ , volume 2067 of LNCS, 2001.

- Johan Bengtsson, Kim G. Larsen, Fredrik Larsson, Paul Pettersson, Wang Yi and Carsten Weise. New Generation of UPPAAL. In _Proceedings of the International Workshop on Software Tools for Technology Transfer_ , 1998

- Johan Bengtsson, Kim G. Larsen, Fredrik Larsson, Paul Pettersson, Wang Yi. UPPAAL in 1995, In _Proceedings of Workshop on Tools and Algorithms for the Construction and Analysis of Systems_ , volume 1055 of LNCS, 1996.

- Johan Bengtsson, Kim G. Larsen, Fredrik Larsson, Paul Pettersson and Wang Yi. UPPAAL - a Tool Suite for Automatic Verification of Real-Time Systems. In _Proceedings of Workshop on Verification and Control of Hybrid Systems III_ , volume 1066 of LNCS, 1995.

--- end of page.page_number=8 ---

## **Contents**

|**Introduction**|**Introduction**|**1**|
|---|---|---|
|1|Background . . . . . . . . . . . . . . . . . . . . . . . . . . .|1|
|2|Timed Automata<br>. . . . . . . . . . . . . . . . . . . . . . . .|2|
|3|Model Checking . . . . . . . . . . . . . . . . . . . . . . . . .|7|
|4|Contributions of This Thesis . . . . . . . . . . . . . . . . . .|9|
|5|Related Work . . . . . . . . . . . . . . . . . . . . . . . . . .|12|
|6|Conclusions and Future Work . . . . . . . . . . . . . . . . . .|15|
|**Paper**|**A: DBM: Structures, Operations and Implementation**|**23**|
|1|Introduction . . . . . . . . . . . . . . . . . . . . . . . . . . .|25|
|2|DBM basics . . . . . . . . . . . . . . . . . . . . . . . . . . .|26|
||2.1<br>Canonical DBMs . . . . . . . . . . . . . . . . . . . .|27|
||2.2<br>Minimal Constraint Systems . . . . . . . . . . . . . .|28|
|3|Operations on DBMs . . . . . . . . . . . . . . . . . . . . . .|31|
||3.1<br>Checking Properties of DBMs . . . . . . . . . . . . .|33|
||3.2<br>Transformations<br>. . . . . . . . . . . . . . . . . . . .|33|
||3.3<br>Normalisation Operations<br>. . . . . . . . . . . . . . .|36|
|4|Zones in Memory . . . . . . . . . . . . . . . . . . . . . . . .|38|
||4.1<br>Storing DBM Elements . . . . . . . . . . . . . . . . .|38|



i

--- end of page.page_number=9 ---

||4.2<br>Placing DBMs in Memory . . . . . . . . . . . . . . .|39|
|---|---|---|
||4.3<br>Storing Sparse Zones . . . . . . . . . . . . . . . . . .|39|
|5|Conclusions . . . . . . . . . . . . . . . . . . . . . . . . . . .|40|
|A|Pseudo-Code<br>. . . . . . . . . . . . . . . . . . . . . . . . . .|42|
|**Paper **|**B: Reachability Analysis of Timed Automata Containing Con-**||
|**straints on Clock Differences**||**45**|
|1|Introduction . . . . . . . . . . . . . . . . . . . . . . . . . . .|47|
|2|Preliminaries<br>. . . . . . . . . . . . . . . . . . . . . . . . . .|50|
||2.1<br>Timed Automata Model<br>. . . . . . . . . . . . . . . .|50|
||2.2<br>Reachability Analysis<br>. . . . . . . . . . . . . . . . .|51|
|3|Constraints on Clock Differences and Normalisation<br>. . . . .|53|
|4|New Normalisation Algorithms . . . . . . . . . . . . . . . . .|54|
||4.1<br>Region Equivalence Refned by Difference Constraints|56|
||4.2<br>The Core of Normalisation . . . . . . . . . . . . . . .|56|
||4.3<br>Algorithm: Normalisation without Zone Splitting . . .|57|
||4.4<br>Algorithm: Normalisation with Zone Splitting . . . . .|58|
|5|Conclusion<br>. . . . . . . . . . . . . . . . . . . . . . . . . . .|63|



|**Paper **|**C: Reducing Memory Usage in Symbolic State-Space Explo-**||
|---|---|---|
|**ration for Timed Systems**||**67**|
|1|Introduction . . . . . . . . . . . . . . . . . . . . . . . . . . .|69|
|2|Preliminaries<br>. . . . . . . . . . . . . . . . . . . . . . . . . .|70|
|3|Representing Symbolic States<br>. . . . . . . . . . . . . . . . .|73|
||3.1<br>Normal Representation . . . . . . . . . . . . . . . . .|73|
||3.2<br>Packed States . . . . . . . . . . . . . . . . . . . . . .|74|
||3.3<br>Packed Zones with Cheap Inclusion Check<br>. . . . . .|75|
|4|Representing the Symbolic State-Space<br>. . . . . . . . . . . .|78|



ii

--- end of page.page_number=10 ---

||4.1<br>Representing WAIT . . . . . . . . . . . . . . . . . . .|78|
|---|---|---|
||4.2<br>Representing PASSED<br>. . . . . . . . . . . . . . . . .|80|
||4.3<br>Supertrace PASSEDfor Timed Automata<br>. . . . . . .|80|
||4.4<br>Hash Compaction for Timed Automata<br>. . . . . . . .|83|
|5|Conclusions . . . . . . . . . . . . . . . . . . . . . . . . . . .|86|
|A|Examples and Experiment Environment . . . . . . . . . . . .|91|
|**Paper**|**D: Partial Order Reductions for Timed Systems**|**93**|
|1|Motivation . . . . . . . . . . . . . . . . . . . . . . . . . . . .|95|
|2|Preliminaries<br>. . . . . . . . . . . . . . . . . . . . . . . . . .|99|
||2.1<br>Networks of Timed Automata . . . . . . . . . . . . .|99|
||2.2<br>Symbolic Global–Time Semantics . . . . . . . . . . .|100|
|3|Partial Order Reduction and Local-Time Semantics . . . . . .|102|
||3.1<br>Symbolic Local-Time Semantics . . . . . . . . . . . .|104|
||3.2<br>Finiteness of the Symbolic Local Time Semantics . . .|106|
|4|Partial Order Reduction in Reachability Analysis<br>. . . . . . .|108|
||4.1<br>Operations on Constraint Systems . . . . . . . . . . .|110|
|5|Conclusion and Related Work<br>. . . . . . . . . . . . . . . . .|111|
|**Paper **|**E: Automated Verifcation of an Audio-Control Protocol using**||
|**UPPAAL**||**115**|
|1|Introduction . . . . . . . . . . . . . . . . . . . . . . . . . . .|117|
|2|Committed Locations . . . . . . . . . . . . . . . . . . . . . .|119|
||2.1<br>An Example<br>. . . . . . . . . . . . . . . . . . . . . .|120|
||2.2<br>Syntax<br>. . . . . . . . . . . . . . . . . . . . . . . . .|121|
||2.3<br>Semantics . . . . . . . . . . . . . . . . . . . . . . . .|122|
|3|Committed Locations in UPPAAL<br>. . . . . . . . . . . . . . .|124|
||3.1<br>The Model-Checking Algorithm . . . . . . . . . . . .|124|



iii

--- end of page.page_number=11 ---

||3.2<br>Space and Time Performance Improvements<br>. . . . .|127|
|---|---|---|
|4|The Audio Control Protocol with Bus Collision . . . . . . . .|128|
|5|A Formal Model of the Protocol<br>. . . . . . . . . . . . . . . .|130|
|6|Verifcation in UPPAAL . . . . . . . . . . . . . . . . . . . . .|133|
|7|Conclusions . . . . . . . . . . . . . . . . . . . . . . . . . . .|135|
|8|Appendix . . . . . . . . . . . . . . . . . . . . . . . . . . . .|139|



iv

--- end of page.page_number=12 ---

Introduction

1

## **Introduction**

## **1 Background**

The computer boom in the last decades has not only given us faster and more advanced equipment for word-processing, banking and scientific computations. The development of small, cheap, and powerful microprocessors has also enabled a range of new application areas. Today, computers are trusted to control all kinds of devices and technical systems used in our society, ranging from stereos and micro-wave ovens to life-support systems and nuclear power-plants. Currently this kind of computer applications, _i.e._ the _embedded systems_ , forms the fastest growing market for microprocessors. In recent years 98%–99% of all produced processors have been used in embedded systems [Hal00]. Only around 2% are used in desktop computers.

In many embedded applications, a computer failure may have dire consequences, such as economical damage, environmental catastrophes and even loss of human lives. Thus it is of great importance that such systems operate correctly, according to their specifications. Traditionally this is accomplished by methods like reviewing of design documents and source code and by extensive simulation and testing of the system and its components. However, this process is often time-consuming and provides only statistical measures of correctness.

As a complement to the traditional methods for obtaining correct software, a large number of mathematically based techniques for reasoning about correctness of computer systems have been proposed in the literature, _e.g._ [Hoa69, Dij75, Hoa78, Rei85, Mil89, Hol91]. The common procedure in all these so called formal methods is to define the system under development in a formal framework and then apply rigorous methods within this framework to prove that the system meets its requirements. However, due to the complexity of reallife systems, applying formal methods is often considered too difficult. A way

--- end of page.page_number=13 ---

Introduction

2

to bridge this gap is to automate the analysis, for instance by using _modelchecking_ [CGP99]. In contrast to manual techniques, model-checking is fully automatic in the sense that the proof showing that a system satisfies a given requirement is constructed by the model-checker without manual interaction.

In this thesis we study and develop techniques for model-checking tools to verify systems where timing is important. The work presented in this thesis is in the context of the model-checker UPPAAL, which is a tool for analysing timing properties of systems modelled as timed automata.

## **2 Timed Automata**

Timed automata [AD90, AD94, HNSY94] is one of the most successful formalisms for describing the timing behaviour of computer systems. Examples of other formal systems with the same purpose, are timed Petri-net models, timed process algebras or real time logics [BD91, RR88, Yi91, NS94, ACD93, AH94, SS95].

## **A Brief Introduction to Timed Automata**

A timed automaton is essentially a finite automaton extended by a set of real valued clocks. All clocks are synchronised in the sense that they start with the value zero when the system is initialised and grow synchronously, with the same rate. The clocks influence the automaton by clock-constraints (guards) on the edges. An edge is only enabled when the values of the clocks satisfies the guard. The automaton can influence the clocks by letting the edges reset a subset of the clocks.

An example of a timed automaton is shown in Figure 1. The timing behaviour of this automaton is controlled by two clocks and . The clock is used to control the small self-loop in the **loop** location. This loop is only possible when the value of is exactly one. The clock controls the execution of the entire automaton. The automaton may leave **start** when is between 10 and 20, it can go from **loop** to **end** when is between 40 and 50, _etc._

In this simple timed-automata model, the guards on the edges only guide the automaton when it decides to act; they can not force it. The example automaton may stay forever in any location, just idling. In the initial work by Alur and Dill [AD90] the problem is solved by introducing Büchi-acceptance conditions;

--- end of page.page_number=14 ---

Introduction

3


![](content_assets/paper.pdf-0015-02.png)


Figure 1: A Timed Automaton

a subset of the locations in the automaton are marked as accepting, and only executions passing through an accepting location infinitely often are considered valid. As an example, consider again the automaton in Figure 1 and assume that **end** is marked as accepting. This implies that all executions of the system enter **end** infinitely many times. This impose implicit conditions on **start** and **loop** . The location **start** must be left when the value of is at most 20, otherwise the automaton would get stuck and never be able to enter **end** . Likewise, the automaton must leave **loop** when is at most 50 to be able to enter **end** .

Büchi-acceptance conditions are theoretically elegant. However, as the example shows, an accepting location has global effects on the automaton, which is inconvenient for modelling and automatic analysis. A more intuitive notion of progress is used in timed safety-automata [HNSY94]. In timed safety-automata, the acceptance conditions are replaced by local timing constraints in each location, that is the so called location invariants. The automaton may only remain in a location as long as the clocks satisfies the invariant condition. This gives a more convenient view of the timing behaviour of particular parts of the automaton. For example, consider the automaton in Figure 2. This timed safetyautomaton corresponds to the Büchi automaton in the previous example. In this automaton the conditions that **start** and **end** must be left when is at most 20 and **loop** must be left when is at most 50 are now stated locally in invariants. This gives a local view of the timing in each location in much more convenient way than Büchi-acceptance. For this reason we will use timed automata with location invariants to describe the timing behaviour of embedded systems.

To model concurrent systems, timed automata is often extended with parallel composition, giving _networks of timed automata_ . In the early work on timedautomata [AD90, HNSY92], parallel composition is treated as logical con-

--- end of page.page_number=15 ---

Introduction

4


![](content_assets/paper.pdf-0016-02.png)


Figure 2: A Timed Safety-Automaton

junction, _i.e._ all processes in a system must synchronise on every action. In this thesis, as well as in UPPAAL, we adopt the parallel composition used in CCS [Mil89], which allows for internal actions in processes, as well as pair-wise synchronisation. An example of a system composed of two timedautomata is presented in Figure 3. The network models a time-dependent lightswitch (to the left) and its user (to the right). The user and the switch communicate by the press labels. The user can press the switch (press!) and the switch waits to be pressed (press?). The product automaton, _i.e._ the automaton describing the combined system is shown in Figure 4. Building the product automaton is an entirely syntactical operation based on the component automata. In UPPAAL, the product automaton is computed on-the-fly during verification.


![](content_assets/paper.pdf-0016-05.png)


Figure 3: Network of Timed Automata

--- end of page.page_number=16 ---

5

Introduction


![](content_assets/paper.pdf-0017-02.png)


Figure 4: Product Automaton for the Network in Figure 3

## **Semantics of Timed Automata**

A state or configuration of a timed automaton has two different parts, the current location and the current values of all clocks. There are two different types of transitions between states. The automaton may either delay for some time (a delay transition), or follow an enabled edge (an action transition). Since clocks in a timed automaton are real-valued the state-space will be infinite and not a good base for automatic verification. However, many verification problems such as language emptiness, reachability analysis and model-checking of timed logics can still be decided by constructing a _region graph_ based on the automaton under consideration and perform the analysis on this graph [AD94, ACD93]. The downside with this solution is the large number of states in the region-graph. As an example, consider Figure 5. The figure shows the possible regions in each location of an automaton with two clocks and . The largest number compared to is 3, and the largest number compared to is 2. In the figure each line segment, each intersection and each area is one region. Thus, the number of possible regions in each location of this example is 60. It also grows rapidly with the number of clocks and the largest constants. In fact, the region graph is exponential in the number of clocks in the system as well as the in largest constants appearing in guards in the automaton.

--- end of page.page_number=17 ---

6

Introduction


![](content_assets/paper.pdf-0018-02.png)


Figure 5: Regions for a System with Two Clocks

A more appealing representation of the state-space for timed automata is obtained by using _zone-graphs_ [Dil89, HNSY94, ACH 95]. Instead of regions, the clock values are represented as constraints on clocks and clock differences. In practice this gives a coarser and thus more compact representation of the state space. The basic operations and algorithms to construct zone-graphs are described in Paper A. As an example, a timed automaton and the corresponding zone graph is shown in Figure 6. We note that for this automaton the zone graph has only eight states. The region-graph for the same example has over fifty.


![](content_assets/paper.pdf-0018-05.png)



![](content_assets/paper.pdf-0018-06.png)



![](content_assets/paper.pdf-0018-07.png)



![](content_assets/paper.pdf-0018-08.png)



![](content_assets/paper.pdf-0018-09.png)



![](content_assets/paper.pdf-0018-10.png)



![](content_assets/paper.pdf-0018-11.png)


Figure 6: A Timed Automaton and the corresponding Zone Graph

The zone-graph of a timed automaton may unfortunately be infinite and verification based on zone-graphs is thus not guaranteed to terminate. As an example, consider the model in Figure 7. In this automaton the value of clock drifts away unboundedly, giving an infinite graph. The solution is to normalise the zones in the zone-graph with respect to the maximum constants in the automaton, that is the so called _-normalisation_ [Rok93, Pet99]. The intuition is that once the value of a clock is larger than the maximum constant in the au-

--- end of page.page_number=18 ---

Introduction

7

tomaton it is no longer significant for the automaton to know its precise value, only that it is above the constant. As an example, the -normalised zone-graph of the automaton in Figure 7 is given in Figure 8. Note that the -normalisation only works for timed automata with guards on individual clocks. For automata with guards on clock differences a more elaborate normalisation procedure is needed (see Paper B).


![](content_assets/paper.pdf-0019-03.png)



![](content_assets/paper.pdf-0019-04.png)



![](content_assets/paper.pdf-0019-05.png)


Figure 7: A Timed Automaton with an Infinite Zone Graph


![](content_assets/paper.pdf-0019-07.png)



![](content_assets/paper.pdf-0019-08.png)


Figure 8: Normalised Zone Graph for the Automaton in Figure 7

## **3 Model Checking**

Model-checking consists of two steps, computing the state-space of the system under consideration, and searching for states, or sets of states that satisfy certain logical properties. The first step can either be performed prior to the search,

--- end of page.page_number=19 ---

Introduction

8

or done _on-the-fly_ during the search process. Computing the state-space on-thefly has an obvious advantage over pre-computing, in that only the part of the state-space needed to prove (or disprove) the property is generated. As an example, consider a system with a million states. Generating the full state-space of this system will take a lot of time and may even be infeasible due to memory requirements. However, if the logical properties of interests can be proven by only examining the first hundred states of the system then an on-the-fly method will only need to generate those states and the result will be almost instantaneous. It should be noted though, that even on-the-fly methods will generate the entire state-space to prove certain properties, _e.g._ invariant properties.

The model-checking procedure itself is based on traversing the state-space in search for states that prove or contradict stated logical properties. As an example, we use one of the model-checking algorithms for timed-automata implemented in UPPAAL (see Algorithm 1).

## **Algorithm 1** Reachability analysis

|PASSED|WAIT|WAIT||
|---|---|---|---|
|**while**WAIT|**do**|||
|take|from WAIT|||
|**if**||**then return**“YES”||
|**if**|for all|PASSED**then**||
|add|to PASSED|||
|**for all**||such that|**do**|
|add||to WAIT||
|**end for**||||
|**end if**||||
|**end while**||||
|**return**“NO”||||



The algorithm is used for verifying _safety properties_ (that something bad will never happen) for networks of timed automata. The properties are given to the algorithm as a set of bad states ( denotes a location in the network and denotes a clock zone). The algorithm will then compute the zone-graph of the system on-the-fly, in search for states intersecting with . The algorithm highlights some of the issues in developing a model-checker for timed automata. First, handling of states, or primarily zones, is crucial to the performance of the model-checker. Thus, devising algorithms and data-structures for zones is a major issue in developing a verification tool for timed automata, which is addressed in Paper A. Second, PASSED holds all states encountered so

--- end of page.page_number=20 ---

Introduction

9

far and its size puts a limit on how large systems we can verify. This makes it important to find compact representations for PASSED. However, since passed is searched each time a new state is processed it is crucial to performance that searching is cheap. This leads to a tradeoff between size and speed. We study this problem in Paper C.

A major obstacle in constructing the state-space of a network of timed automata is the so called state-explosion problem. The problem appears in all kinds of model-checkers, and the source of the problem is the practice of modelling concurrent systems using parallel composition of several automata. The effect is a rapid growth of the explored state-space due to the fact that each possible interleaving of the automata will be taken into account by the analysis.

A method for reducing the state-space used in model-checkers for untimed systems is partial-order reductions. With this technique the state-space is reduced by removing interleavings of independent transitions and choose one representative. However, in timed-automata the number of independent transitions is much less than in the untimed case due to the tight synchronisation of time. One way of breaking this synchronisation, without affecting stated reachability properties, is presented in Paper D.

Finally we shall point out that a powerful verification engine is not enough to get a successful tool and there are other issues in building verification tools. For a tool to be widely used it requires substantial work on the user interface. For instance, in UPPAAL a lot of effort has been put on improving the user interface. However, such issues are not the topic of this thesis.

## **4 Contributions of This Thesis**

The main contributions of this thesis are in the development and implementation of UPPAAL, a tool-suite for timed-automata developed in collaboration between Uppsala University and Aalborg University. The first version of UPPAAL was released in spring 1995, and was then the first verification tool for timed automata where the system model could be drawn graphically (What You See Is What You Verify). In 1996, another step was taken in the same direction, when UPPAAL was equipped with a simulator that enable the user to test system models interactively and to visualise counterexamples generated by the model-checker. In 1999, the architecture of UPPAAL was completely changed, the tool was separated into two parts: A graphical user interface and a verification engine. Among other things this change enabled the GUI and the

--- end of page.page_number=21 ---

Introduction

10

verification engine to be run on separate machines, _e.g._ running the GUI on a local work-station and the verification engine on a large server. Today UPPAAL is one of the most popular tools for timed automata and it has been downloaded by over 1300 different users from over 70 countries.

The performance of the verification engine has always been a key issue when developing UPPAAL. This is also the part where most of the contributions described in this thesis are located.

## **A DBM Package: Data-Structures and Operations [Paper A,B]**

Zones are the most important entities in a model-checker for timed systems and their representation and implementation are crucial to the performance. In implementing UPPAAL we discovered a number of techniques to improve performance of zone operations. In this thesis we present our experiences in form of a cook-book on Difference Bound Matrices [Dil89]. We describe all primitive operations and data-structures for zones needed to implement state-space exploration for time-automata in both forwards and backwards analysis, including operations for checking properties of zones, for computing the effect of delaying and resetting of clocks, and for constraining a zone with respect to a guard. We also present how to normalise the clock-zones with respect to guards in the automaton to guarantee that the model-checking procedure terminates. In particular we discovered that the existing -normalisation algorithms published in the literature do not work for timed-automata with guards on clock-differences. We have developed two new normalisation algorithms for automata that may contain constraints on clock differences.

## **Low-Level Optimisations [Paper C]**

The performance of UPPAAL has been greatly improved by low-level optimisations on its central algorithms and data-structures. In this thesis we develop and evaluate a number of techniques to minimise memory and time consumption. The techniques are implemented in UPPAAL and we believe that they are generic and applicable to model-checking of timed-systems in general.

We present two different methods for packing states. First, we code the entire state as one large number using a multiply-and-add algorithm. This method yields a representation that is canonical and minimal in terms of memory usage but the performance for inclusion checking between states is poor. The second method is mainly intended to use for the timing part of the state and it is based on concatenation of bit strings. Using a special concatenation of the bit string

--- end of page.page_number=22 ---

Introduction

11

representation of the constraints in a zone, ideas from [PS80] can be used to implement fast inclusion checking between packed zones.

The problem representing large state-spaces is addressed in two different ways. First, to get rid of states that do not need to be explored, as early as possible, we introduce inclusion checking already in the data structure keeping the states waiting to be explored. We also describe an implementation where time, as well as memory, is saved by this technique. Second, we investigate how supertrace [Hol91] and hash-compaction [WL93, SD95b] methods can be applied to timed systems. We present a variant of the hash compaction method, that allows termination of branches in the search tree based on probable inclusion checking between states. These techniques have been implemented in the UPPAAL tool, evaluated and compared by real-life examples; their strengths and weaknesses are described.

## **Partial Order Reduction [Paper D,E]**

A major problem in automatic verification is the large number of states introduced by modelling concurrent events as interleaved transitions. In many cases, the order of the transitions are irrelevant for the investigated properties and one specific order can be chosen to represent all. In this thesis we address this problem in a setting of timed systems. We present a notion of committed locations for timed automata. Committed locations are annotations that can be used for not only modelling of intermediate states within atomic transitions, but also guiding the model checker to ignore unnecessary interleavings in state-space exploration. During modelling, intermediate locations in sequences of internal actions can be marked as committed. This prohibits delay in the locations and allows its transitions to be interleaved only with transitions of committed locations in other automata in the network. We present a modified algorithm for state space exploration for networks of timed automata which generate a reduced number of states when committed locations are used. Our experimental results demonstrate significant time and space-savings for a number of applications. For example, the audio control protocol presented in Paper E could not have been verified in 1995 without using committed locations.

Committed location is a simple case of getting rid of unnecessary interleavings in sequences of transitions without delays. Naturally, we want to extend the notion to sequences with non-zero delays. However, due to the tight synchronisation of time, delay in timed-automata has a global effect. To resolve this issue, we introduce a notion of local-time and let local clocks in each process advance independently of clocks in other processes. To avoid communication

--- end of page.page_number=23 ---

Introduction

12

between processes with different notion of the current time we require processes to resynchronise their local time scales whenever they communicate. A symbolic local-time semantics is developed in terms of predicate transformers, which enjoys the desired property that two predicate transformers are independent if they correspond to disjoint transitions in different processes. This allows existing partial order reduction techniques to be applied to the problem of reachability analysis for timed systems.

## **5 Related Work**

In the past years, a large number of model-checkers have been developed by researchers for different application areas. For examples, we mention SPIN [Hol91, Hol97] for communication protocols and Mur [DDHY92] for concurrent and reactive systems, UPPAAL [LPY97, ABB 01] and KRONOS [DOTY95, Yov97, BDM 98] for timed systems, and HYTECH [HHWT97] for hybrid systems. These tools have all been successfully applied to industrial-size case studies, _e.g._ [HLP98, JMMS98, SD95a, MMS97, LPY98, HSLL97, TY98, HWT96]. In this section we summarise the most successful and known techniques implemented in these tools.

**Partial-order reduction:** Partial-order methods [God90, Val90, Pel93] are based on the observation that in many cases the exact ordering of events affects neither the examined properties nor how the system evolves in the future. In these cases all equivalent orderings can be represented by one single ordering. For timed-automata there are two different approaches to applying partial order reductions. The first approach was introduced by Pagani in [Pag96] and later improved by Dams _et. al._ [DGKK98]. It is based on the global-time semantics of timed automata. This limits the possible reductions in that only transitions that can occur in exactly the same time-interval can be independent. The second approach is the local-time approach proposed in Paper D of this thesis. In [Min99], Minea extends our result for reachability analysis to LTL modelchecking. Minea also shows that standard normalisation techniques for timingconstraints are applicable also in local-time semantics.

**Symmetry reductions:** Symmetry reduction [HJJJ84, ID96, ES97] is a method for exploiting the fact that many system-models have a large number of identical processes. It is often the case that these identical processes may be interchanged without noticeably affecting the system. As an example, in a communication protocol it may not matter if process A is sending and process B

--- end of page.page_number=24 ---

Introduction

13

is receiving or the other way around. In a model-checker this is exploited by defining equivalence classes for states based on different permutations of the identical processes. The model-checking algorithm is then applied to the graph of equivalence classes instead of the full state-space. As examples. we mention that this technique has been implemented in the tools Mur [ID96] and SGM [HW98, WH02].

**Symbolic model-checking:** The key idea of symbolic model-checking is in representing and manipulating sets of states in terms of logical formulae. The best known symbolic technique, introduced in [BCM 92], describe states and transitions as propositional formulae and use BDDs [Bry86] to store and manipulate them. The so called bounded model-checking is introduced in [BCCZ99]. In this work, the task of checking if a system-model has a certain logical property is transformed into checking satisfiability for a series of propositional formulae. Symbolic techniques for timed-systems are all based on zones [Dil89, HNSY94, AHH96, ACH 95, YPD94], where sets of clock-values are represented and manipulated using clock constraints. This is the main topic of this thesis.

**Approximation methods:** Approximation methods are aimed at systems that are too large to be handled by precise methods, at the price that some results are inconclusive. There are two different types of approximation methods, underapproximations where part of the reachable state-space may be considered not reachable by the model-checker, and over-approximations where non-reachable states may be considered reachable by algorithm. Two examples of underapproximation are Supertrace [Hol91] and hash-compaction [WL93, SD95b]. These methods may conclude erroneously during verification that some unexplored state has been visited before. Thus, with under-approximations, a claim that invariant properties hold is inconclusive, since states violating the property may be lost in the approximation. Over-approximation techniques are often combined with symbolic model-checking. Often, the union of two symbolicstates can not be precisely represented by a single formula while it is possible to construct a formula including two symbolic states. In [Bal96] this type of method is applied to verification of timed automata. In the paper the convexhull of time-zones are used as an approximation of union. In [WT94], Wong-Toi presents techniques for refining the results obtained by over-approximations by combining the results from forwards and backwards analysis.

**Efficient Representation of Clock Constraints:** In a verification tool, a large fraction of memory used during verification is spent on storing clock constraints. In the literature there are a number of techniques addressing this prob-

--- end of page.page_number=25 ---

Introduction

14

lem. In [DY96] live-range analysis is used to reduce the number of clocks in a model. The control-structure of the system-model is analysed to compute the set of active clocks for each location. To save space, only timing information regarding active clocks are stored. Another approach is taken in [LLPY97]. This work is based on the observation that the DBM representation of a time zone often contains redundant information, _i.e._ the same set of clock values can be represented using much fewer constraints. The paper presents an algorithm for computing the minimal set of constraints for a given DBM.

Inspired by the success of using BDDs to encode state-spaces in hardware verification, a number of similar techniques for representing clock zones were developed. In [Bal96], Balarin present a schema for encoding DBMs using DBBs. He also develop algorithms for performing essential DBM operations directly on the BDD. In [ABK 97], Asarin _et. al._ introduce Numerical Decision Diagrams (NDDs), a technique for representing sets of regions from the region-graph of timed automata as BDDs. The problem with both these representations is their sensitivity to time-granularity. This problem is not present for Clock Difference Diagrams (CDDs) [LPWY99, BLP 99] and Difference Decision Diagrams (DDDs) [MLAH99a, MLAH99b], which are two similar types of decision diagrams based on difference constraints. They allow for nonconvex unions of zones to be represented by a single diagram, and the main difference is that in DDDs each node represents a single difference constraint, while a node in a CDD represents all difference constraints on a clock-pair. Thus, DDDs will, in general, have more nodes than the corresponding CDD, while the nodes in a CDD have a larger and variable number of edges.

**Low-Level Optimisations:** For many applications, it is not feasible to store all explored states in main memory. In [SD98], Stern and Dill present a method for storing PASSED on magnetic disk. To compensate for the increased time to access PASSED, they collect a large number of states in WAIT and check all of them in one sequential sweep through PASSED. Other alternatives when dealing with large state-spaces is to store only enough states to guarantee termination. In [LLPY97] static analysis of the system-model is used to compute the set of loop-entry location in the processes. A state is then stored in PASSED only if one of the processes enter such a location. This guarantee that at least one state in each dynamic loop will be present on PASSED and thus termination is ensured. A method for throwing identifying and removing states that no longer can be revisited is presented in [CKM01]. A progress measure is used by the model-checker to identify such states.

--- end of page.page_number=26 ---

15

Introduction

## **6 Conclusions and Future Work**

This thesis summarises our experiences in developing and implementing UPPAAL. We have studied and developed techniques to improve the performance of UPPAAL in the verification process. Our main contributions are in three directions. First we have presented a DBM package including all data-structures and operations needed in symbolic state-space exploration of timed automata. We hope that the included reports may serve as a cook-book for tool developers of timed-systems. Second, we have presented and implemented a collection of low-level optimisations on the central algorithms and data-structures of UPPAAL. They have given significant performance improvements for the tool. Though these techniques are developed for UPPAAL, we believe that they are generic and applicable to other model-checkers for timed-systems. As the third contribution we have presented partial-order reduction techniques for timed systems. The notion of committed locations has been a useful mechanism for not only modelling atomic sequences but also guiding the model-checker to avoid redundant interleavings in state-space exploration. Though the notion of committed locations has been generalised to give a local-time semantics for networks of timed automata, which allows for partial order reductions in statespace exploration of timed systems, the technique has not yet been fully explored. This is a challenging area for future work. The local-time semantics is just a step on the way. A challenge is to develop an efficient implementation of the technique.

The work presented in this thesis can be extended in several directions. Hierarchical extensions to timed automata is a direction that is currently being pursued within the UPPAAL group. A challenging problem is how to take advantage of the hierarchical structures in state-space exploration. As future work, we will further study techniques to reduce memory requirements without losing performance in time, _e.g._ to develop packing methods and hash functions for zones, that preserve inclusion checking.

## **References**

- [ABB 01] Tobias Amnell, Gerd Behrmann, Johan Bengtsson, Pedro R. D’Argenio, Alexandre David, Ansgar Fehnker, Thomas Hune, Bertrand Jeannet, Kim G. Larsen, M. Oliver Möller, Paul Pettersson, Carsten Weise, and Wang Yi. UPPAAL - Now, Next, and Future. In _Modelling and Verification of Parallel Processes_ , volume 2067 of _Lecture Notes in Computer Science_ , pages 100–125. Springer-Verlag, 2001.

--- end of page.page_number=27 ---

16

Introduction

- [ABK 97] Eugene Asarin, Marius Bozga, Alain Kerbrat, Oded Maler, Amir Pnueli, and Anne Rasse. Data structures for the verification of timed automata. In _Proceedings, Hybrid and Real-Time Systems_ , volume 1201 of _Lecture Notes in Computer Science_ , pages 346–360. Springer-Verlag, 1997.

- [ACD93] Rajeev Alur, Costas Courcoubetis, and David L. Dill. Model-checking in dense real-time. _Journal of Information and Computation_ , 104(1):2–34, 1993.

- [ACH 95] Rajeev Alur, Costas Courcoubetis, Nicholas Halbwachs, Thomas A. Henzinger, Pei-Hsin Ho, Xavier Nicollin, Alfredo Olivero, Joseph Sifakis, and Sergio Yovine. The algorithmic analysis of hybrid systems. _Journal of Theoretical Computer Science_ , 138(1):3–34, 1995.

- [AD90] Rajeev Alur and David L. Dill. Automata for modeling real-time systems. In _Proceedings, Seventeenth International Colloquium on Automata, Languages and Programming_ , volume 443 of _Lecture Notes in Computer Science_ , pages 322–335. Springer-Verlag, 1990.

- [AD94] Rajeev Alur and David L. Dill. A theory of timed automata. _Journal of Theoretical Computer Science_ , 126(2):183–235, 1994.

- [AH94] Rajeev Alur and Thomas A. Henzinger. A really temporal logic. _Journal of the ACM_ , 41(1):181–204, 1994.

- [AHH96] Rajeev Alur, Thomas A. Henzinger, and Pei-Hsin Ho. Automatic symbolic verification of embedded systems. _IEEE Transactions on Software Engineering_ , 22:181–201, 1996.

- [Bal96] Felice Balarin. Approximate reachability analysis of timed automata. In _Proceedings, 17_ th _IEEE Real-Time Systems Symposium_ . IEEE Computer Society Press, 1996.

- [BCCZ99] Armin Biere, Alessandro Cimatti, Edmund M. Clarke, and Yunshan Zhu. Symbolic model checking without BDDs. In _Proceedings, Fifth International Conference on Tools and Algorithms for the Construction and Analysis of Systems_ , volume 1579 of _Lecture Notes in Computer Science_ . Springer-Verlag, 1999.

- [BCM 92] J. R. Burch, E. M. Clarke, K. L. McMillan, D. L. Dill, and L. J. Hwang. Symbolic model checking: states and beyond. _Journal of Information and Computation_ , 98(2):142–170, 1992.

- [BD91] Bernard Berthomieu and Michel Diaz. Modeling and verification of timed dependent systems using timed petri nets. _IEEE Transactions on Software Engineering_ , 17(3):259–273, 1991.

- [BDM 98] Marius Bozga, Conrado Daws, Oded Maler, Alfredo Olivero, Stavros Tripakis, and Sergio Yovine. Kronos: a model-checking tool for realtime systems. In _Proceedings, Tenth International Conference on Computer Aided Verification_ , volume 1427 of _Lecture Notes in Computer Science_ . Springer-Verlag, 1998.

--- end of page.page_number=28 ---

Introduction

17

- [BLP 99] Gerd Behrmann, Kim G. Larsen, Justin Pearson, Carsten Weise, and Wang Yi. Efficient timed reachability analysis using clock difference diagrams. In _Proceedings, Eleventh International Conference on Computer Aided Verification_ , volume 1633 of _Lecture Notes in Computer Science_ , pages 341–353. Springer-Verlag, 1999.

- [Bry86] Randal E. Bryant. Graph-based algorithm for boolean function manipulation. _IEEE Transactions on Computers_ , C-35(8):677–691, 1986.

- [CGP99] Edmund M. Clarke, Orna Grumberg, and Doron A. Peled. _Model Checking_ . The MIT Press, 1999.

- [CKM01] Søren Christensen, Lars Michael Kristensen, and Thomas Mailund. A sweep-line method for state space exploration. In _Proceedings, Seventh International Conference on Tools and Algorithms for the Construction and Analysis of Systems_ , volume 2031 of _Lecture Notes in Computer Science_ , pages 450–464. Springer-Verlag, 2001.

- [DDHY92] David L. Dill, Andreas J. Drexler, Alan J. Hu, and C. Han Yang. Protocol verification as a hardware design aid. In _Proceedings, IEEE International Conference on Computer Design, VLSI in Computers and Processors_ , pages 522–525. IEEE Computer Society Press, 1992.

- [DGKK98] Dennis Dams, Rob Gerth, Bart Knaack, and Ruurd Kuiper. Partial-order reduction techniques for real-time model checking. _Formal Aspects of Computing_ , 10(5–6):469–482, 1998.

- [Dij75] E. W. Dijkstra. Guarded commands, nondeterminacy and formal derivation of programs. _Communications of the ACM_ , 18(8):453–457, 1975.

- [Dil89] David L. Dill. Timing assumptions and verification of finite-state concurrent systems. In _Proceedings, Automatic Verification Methods for Finite State Systems_ , volume 407 of _Lecture Notes in Computer Science_ , pages 197–212. Springer-Verlag, 1989.

- [DOTY95] Conrado Daws, Alfredo Olivero, Stavros Tripakis, and Sergio Yovine. The tool Kronos. In _Proceedings, Hybrid Systems III: Verification and Control_ , volume 1066 of _Lecture Notes in Computer Science_ . SpringerVerlag, 1995.

- [DY96] Conrado Daws and Sergio Yovine. Reducing the number of clock variables of timed automata. In _Proceedings, 17_ th _IEEE Real-Time Systems Symposium_ . IEEE Computer Society Press, 1996.

- [ES97] E. Allen Emerson and A. Prasad Sistla. Using symmetry when modelchecking under fairness assumptions: An automata theoretic approach. _ACM Transactions on Programming Languages and Systems_ , 19(4), 1997.

--- end of page.page_number=29 ---

Introduction

18

- [God90] Patrice Godefroid. Using partial orders to improve automatic verification methods. In _Proceedings, Second International Conference on Computer Aided Verification_ , volume 531 of _Lecture Notes in Computer Science_ , pages 176–185. Springer-Verlag, 1990.

- [Hal00] Tom R. Halfhill. Embedded market breaks new ground. _Microprocessor Report_ , January 2000.

- [HHWT97] Thomas A. Henzinger, Pei-Hsin Ho, and Howard Wong-Toi. HYTECH: A model checker for hybrid systems. _Journal on Software Tools for Technology Transfer_ , pages 110–122, 1997.

- [HJJJ84] Peter Huber, Arne M. Jensen, Leif O. Jespen, and Kurt Jensen. Towards reachability trees for high-level petri nets. In _Proceedings, Advances on Petri Nets ’84_ , volume 188 of _Lecture Notes in Computer Science_ . Springer-Verlag, 1984.

- [HLP98] Klaus Havelund, Mike Lowry, and John Penix. Formal analysis of a space craft controller using Spin. In _Proceedings, Fourth International SPIN Workshop_ , 1998. Proccedings available online. URL: http://netlib.bell-labs.com/netlib/spin/ws98/program.html.

- [HNSY92] Thomas A. Henzinger, Xavier Nicollin, Joseph Sifakis, and Sergio Yovine. Symbolic model checking for real-time systems. In _Proceedings, Seventh Annual IEEE Symposium on Logic in Computer Science_ , pages 394–406, 1992.

- [HNSY94] Thomas A. Henzinger, Xavier Nicollin, Joseph Sifakis, and Sergio Yovine. Symbolic model checking for real-time systems. _Journal of Information and Computation_ , 111(2):193–244, 1994.

- [Hoa69] C. A. R. Hoare. An axiomatic basis for computer programming. _Communications of the ACM_ , 12(10):576–580, 1969.

- [Hoa78] C. A. R. Hoare. Communicating sequential processes. _Communications of the ACM_ , 21(8):666–677, 1978.

- [Hol91] Gerard J. Holzmann. _Design and Validation of Computer Protocols_ . Prentice-Hall, 1991.

- [Hol97] Gerard J. Holzmann. The model checker Spin. _IEEE Transactions on Software Engineering_ , 23(5):279–295, 1997.

- [HSLL97] Klaus Havelund, Arne Skou, Kim G. Larsen, and Kristian Lund. Formal modelling and analysis of an audio/video protocol: An industrial case study using UPPAAL. In _Proceedings, 18_ th _IEEE Real-Time Systems Symposium_ , pages 2–13. IEEE Computer Society Press, 1997.

- [HW98] Pao-Ann Hsiung and Farn Wang. A state-graph manipulator tool for realtime system specification and verification. In _Proceedings, Fifth International Conference on Real-Time Computing Systems and Applications_ , 1998.

--- end of page.page_number=30 ---

Introduction

19

- [HWT96] Thomas A. Henzinger and Howard Wong-Toi. Using HYTECH to synthesize control parameters for a steam boiler. In _Formal Methods for Industrial Applications: Specifying and Programming the Steam Boiler Control_ , number 1165 in Lecture Notes in Computer Science, pages 265–282. Springer-Verlag, 1996.

- [ID96] C. Norris Ip and David L. Dill. Better verification through symmetry. _Journal of Formal Methods in System Design_ , 9, 1996.

- [JMMS98] Wil Janssen, Radu Mateescu, Sjouke Mauw, and Jan Springintveld. Verifying business processes using SPIN. In _Proceedings, Fourth International SPIN Workshop_ , 1998. Proccedings available online. URL: http://netlib.bell-labs.com/netlib/spin/ws98/program.html.

- [LLPY97] Kim G. Larsen, Fredrik Larsson, Paul Pettersson, and Wang Yi. Efficient verification of real-time systems: Compact data structure and state space reduction. In _Proceedings, 18_ th _IEEE Real-Time Systems Symposium_ , pages 14–24. IEEE Computer Society Press, 1997.

- [LPWY99] Kim G. Larsen, Justin Pearson, Carsten Weise, and Wang Yi. Clock difference diagrams. _Nordic Journal of Computing_ , 1999.

- [LPY97] Kim G. Larsen, Paul Petterson, and Wang Yi. UPPAAL in a nutshell. _Journal on Software Tools for Technology Transfer_ , 1997.

- [LPY98] Magnus Lindahl, Paul Pettersson, and Wang Yi. Formal Design and Analysis of a Gear-Box Controller. In _Proceedings, Fourth Workshop on Tools and Algorithms for the Construction and Analysis of Systems_ , number 1384 in Lecture Notes in Computer Science, pages 281–297. Springer-Verlag, 1998.

- [Mil89] Robin Milner. _Communication and Concurrency_ . Prentice Hall International Series in Computer Science. Prentice Hall, 1989.

- [Min99] Marius Minea. _Partial Order for Verification of Timed Systems_ . PhD thesis, School of Computer Science, Carnegie Mellon University, 1999.

- [MLAH99a] Jesper Møller, Jakob Lichtenberg, Henrik Reif Andersen, and Henrik Hulgaard. Difference decision diagrams. In _Proceedings, 13th International Workshop on Computer Science Logic_ , volume 1683 of _Lecture Notes in Computer Science_ . Springer-Verlag, 1999.

- [MLAH99b] Jesper Møller, Jakob Lichtenberg, Henrik Reif Andersen, and Henrik Hulgaard. On the symbolic verification of timed systems. Technical Report IT-TR-1999-024, Department of Information Technology, Technical University of Denmark, 1999.

- [MMS97] John C. Mitchell, Mark Mitchell, and Ulrich Stern. Automated analysis of cryptographic protocols using Mur . In _Proceedings, 1997 Conference on Security and Privacy_ , pages 141–153. IEEE Computer Society Press, 1997.

--- end of page.page_number=31 ---

Introduction

20

- [NS94] Xavier Nicollin and Joseph Sifakis. The algebra of timed processes, ATP: Theory and application. _Journal of Information and Computation_ , 114(1):131–178, 1994.

- [Pag96] Florence Pagani. Partial orders and verification of real-time systems. In _Proceedings, Fourth International Symposium on Formal Techniques in Real-Time and Fault-Tolerant Systems._ , volume 1135 of _Lecture Notes in Computer Science_ , pages 327–346. Springer-Verlag, 1996.

- [Pel93] Doron Peled. All from one, one for all: on model checking using representatives. In _Proceedings, Fifth International Conference on Computer Aided Verification_ , volume 697 of _Lecture Notes in Computer Science_ , pages 409–423. Springer-Verlag, 1993.

- [Pet99] Paul Pettersson. _Modelling and Verification of Real-Time Systems Using Timed Automata: Theory and Practice_ . PhD thesis, Uppsala University, 1999.

- [PS80] Wolfgang J. Paul and Janos Simon. Decision trees and random access machines. In _Logic and Algorithmic_ , volume 30 of _Monographie de L’Enseignement Mathématique_ , pages 331–340. L’Enseignement Mathématique, Université de Genève, 1980.

- [Rei85] Wolfgang Reisig. Petri nets. An Introduction. In _EATCS Monographs on Theoretical Compute Science_ , volume 4. Springer Verlag, 1985.

- [Rok93] Tomas Gerhard Rokicki. _Representing and Modeling Digital Circuits_ . PhD thesis, Stanford University, 1993.

- [RR88] G. M. Reed and A. W. Roscoe. A timed model for communicating sequential processes. _Theoretical Computer Science_ , 58(1-3):249–261, 1988.

- [SD95a] Ulrich Stern and David L. Dill. Automatic verification of the SCI cache coherence protocol. In _Correct Hardware Design and Verification Methods: IFIP WG10.5 Advanced Research Working Conference Proceedings_ , 1995.

- [SD95b] Ulrich Stern and David L. Dill. Improved probabilistic verification by hash compaction. In _Correct Hardware Design and Verification Methods: IFIP WG10.5 Advanced Research Working Conference Proceedings_ , 1995.

- [SD98] Ulrich Stern and David L. Dill. Using magnetic disk instead of main memory in the Mur verifier. In _Proceedings, Tenth International Conference on Computer Aided Verification_ , volume 1427 of _Lecture Notes in Computer Science_ . Springer-Verlag, 1998.

- [SS95] Oleg V. Sokolsky and Scott A. Smolka. Local model checking for realtime systems. In _Proceedings, Seventh International Conference on Computer Aided Verification_ , volume 939 of _Lecture Notes in Computer Science_ . Springer-Verlag, 1995.

--- end of page.page_number=32 ---

Introduction

21

- [TY98] Stavros Tripakis and Sergio Yovine. Verification of the fast reservation protocol with delayed transmission using the tool Kronos. In _Proceedings, Fourth IEEE Real-Time Technology and Applications Symposium_ . IEEE Computer Society Press, 1998.

- [Val90] Antti Valmari. A stubborn attack on state explosion. In _Proceedings, Second International Conference on Computer Aided Verification_ , volume 531 of _Lecture Notes in Computer Science_ , pages 156–165. SpringerVerlag, 1990.

- [WH02] Farn Wang and Pao-Ann Hsiung. Efficient and user-friendly verification. _IEEE Transactions on Computers_ , 51(1):61–83, 2002.

- [WL93] Pierre Wolper and Dennis Leroy. Reliable hashing without collision detection. In _Proceedings, Fifth International Conference on Computer Aided Verification_ , volume 697 of _Lecture Notes in Computer Science_ , pages 59–70. Springer-Verlag, 1993.

- [WT94] Howard Wong-Toi. _Symbolic Approximation for Verifying Real-Time Systems_ . PhD thesis, Stanford University, 1994.

- [Yi91] Wang Yi. CCS + time = an interleaving model for real time systems. In _Proceedings, Eighteenth International Colloquium on Automata, Languages and Programming_ , volume 510 of _Lecture Notes in Computer Science_ . Springer-Verlag, 1991.

- [Yov97] Sergio Yovine. Kronos: a verification tool for real-time systems. _Journal on Software Tools for Technology Transfer_ , 1, October 1997.

- [YPD94] Wang Yi, Paul Petterson, and Mats Daniels. Automatic verification of real-time communicating systems by constraint-solving. In _Proceedings, Seventh International Conference on Formal Description Techniques_ , pages 223–238, 1994.

--- end of page.page_number=33 ---

--- end of page.page_number=34 ---

**Paper A: DBM: Structures, Operations and Implementation**

Johan Bengtsson.

--- end of page.page_number=35 ---

--- end of page.page_number=36 ---

25

DBM: Structures, Operations and Implementation

## **DBM: Structures, Operations and Implementation**

## Johan Bengtsson

**Abstract.** A key issue when building a verification tool for timed systems is how to handle timing constraints arising in state-space exploration. Difference Bound Matrices (DBMs) is a well-studied technique for representing and manipulating timing constraints. The goal of this paper is to provide a cook-book and a software package for the development of verification tools using DBMs. We present all operations on DBMs needed in symbolic state-space exploration for timed automata, as well as data-structures and techniques for efficient implementation.

## **1 Introduction**

During the last ten years, timed automata [AD90, AD94] has evolved as a common model for timed systems and one of the reasons behind its success is the availability of verification tools, such as UPPAAL [LPY97, ABB 01] and KRONOS [DOTY95, Yov97], that can verify industrial-size applications modelled as timed automata. The major problem in automatic verification is the large number states induced by the state explosion. For timed systems this problem has an even larger impact since both the number of states and the size of a single state are significantly larger than in the untimed case due to timing constraints. This makes devising data-structures for states and timing constraints one of the key challenges in developing verification tools for timed systems.

In this paper we describe a software package for representing timing constraints, arising from state space exploration of timed systems, as difference bound matrices [Dil89]. The package is based on the DBM implementation of [BL96] but it has been significantly improved using implementation experiences gained from developing the current version of UPPAAL. The paper is intended as a cook-book for developers of verification tools and the goal is to provide a basis for the implementation of state-of-the-art verification tools.

The paper is organised as follows: In Section 2 we introduce the DBM structure and its canonical form; we also describe how to find the minimal number of constraints needed to represent the same set of clock assignments as a given DBM. Section 3 lists all DBM operations needed to implement a verification

--- end of page.page_number=37 ---

DBM: Structures, Operations and Implementation

26

tool such as UPPAAL together with efficient algorithms for these operations. Some suggestions on how to store the structures in memory are given in Section 4 and finally Section 5 concludes the paper.

## **2 DBM basics**

The key objects for representing timing information in symbolic state-space exploration for timed systems are a special class of constraint systems referred to as difference-bound constraint-systems or, more commonly, zones. A zone for a set of clocks is a conjunction of atomic constraints of the form and where , and . What make zones so important is their simple structure and that the set of zones is closed with respect to the strongest postcondition of all operations needed in state-space generation.

Since zones are frequently used objects, their representation is a major issue when building a verification tool for timed automata. In this section we describe the basic concepts behind Difference Bound Matrices (DBM) [Dil89], which is one of the most effective data structures for zones.

To have a unified form for clock constraints we introduce a reference clock with constant value 0. Let . Then any zone can be rewritten as a conjunction of constraints of the form for , and .

Naturally, if the rewritten zone has two constraints on the same pair of variables only the tightest of them is significant. Thus, a zone can be represented using at most atomic constraints of the form such that each pair of clocks is mentioned only once. We can then store zones using matrices where each element in the matrix corresponds to an atomic constraint. Since each element in such a matrix represents a bound on the difference between two clocks, we call them _Difference Bound Matrices_ (DBMs). In the following presentation we let denote element in the DBM representing the zone .

To compute the DBM representation for a zone , we start by numbering all clocks in to assign one row and one column in the matrix to each clock. The row is used for storing lower bounds on the difference between the clock and all other clocks while the column is used for upper bounds. The elements in the matrix are then computed in three steps.

--- end of page.page_number=38 ---

DBM: Structures, Operations and Implementation

27


![](content_assets/paper.pdf-0039-02.png)


- For each bound in , in , let .


![](content_assets/paper.pdf-0039-04.png)


- For each clock difference that is unbounded in , let . Where is a special value denoting that no bound is present.


![](content_assets/paper.pdf-0039-06.png)


- Finally add the implicit constraints that all clocks are positive, _i.e._ , and that the difference between a clock and itself is always 0, _i.e._ .

As an example, consider the zone . To construct the matrix representation of , we number the clocks in the order . The resulting matrix representation is shown below:


![](content_assets/paper.pdf-0039-09.png)



![](content_assets/paper.pdf-0039-10.png)



![](content_assets/paper.pdf-0039-11.png)



![](content_assets/paper.pdf-0039-12.png)



![](content_assets/paper.pdf-0039-13.png)



![](content_assets/paper.pdf-0039-14.png)



![](content_assets/paper.pdf-0039-15.png)



![](content_assets/paper.pdf-0039-16.png)



![](content_assets/paper.pdf-0039-17.png)



![](content_assets/paper.pdf-0039-18.png)



![](content_assets/paper.pdf-0039-19.png)



![](content_assets/paper.pdf-0039-20.png)



![](content_assets/paper.pdf-0039-21.png)



![](content_assets/paper.pdf-0039-22.png)



![](content_assets/paper.pdf-0039-23.png)



![](content_assets/paper.pdf-0039-24.png)



![](content_assets/paper.pdf-0039-25.png)



![](content_assets/paper.pdf-0039-26.png)



![](content_assets/paper.pdf-0039-27.png)



![](content_assets/paper.pdf-0039-28.png)



![](content_assets/paper.pdf-0039-29.png)



![](content_assets/paper.pdf-0039-30.png)



![](content_assets/paper.pdf-0039-31.png)



![](content_assets/paper.pdf-0039-32.png)



![](content_assets/paper.pdf-0039-33.png)



![](content_assets/paper.pdf-0039-34.png)



![](content_assets/paper.pdf-0039-35.png)



![](content_assets/paper.pdf-0039-36.png)



![](content_assets/paper.pdf-0039-37.png)



![](content_assets/paper.pdf-0039-38.png)



![](content_assets/paper.pdf-0039-39.png)



![](content_assets/paper.pdf-0039-40.png)



![](content_assets/paper.pdf-0039-41.png)



![](content_assets/paper.pdf-0039-42.png)



![](content_assets/paper.pdf-0039-43.png)



![](content_assets/paper.pdf-0039-44.png)



![](content_assets/paper.pdf-0039-45.png)


To manipulate DBMs efficiently we need two operations on bounds: comparison and addition. We define that , if and . Further we define addition as , and .

## **2.1 Canonical DBMs**

Usually there are an infinite number of zones sharing the same solution set. However, for each family of zones with the same solution set there is a unique constraint system where no atomic constraint can be strengthened without losing solutions. We say that such a zone is _closed under entailment_ or just _closed_ . Since there is a unique closed zone for each solution set we use closed zones as canonical representation of entire families of zones.

To compute the closed representative of a given zone we need to derive the tightest constraint on each clock difference. To solve this problem, we use a graph-interpretation of zones. If we see zones as a weighted graphs where the clocks in are nodes and the atomic constraints are edges, deriving bounds corresponds to adding weights along paths in the graph. Note that DBMs form adjacency matrices for this graph-interpretation.

--- end of page.page_number=39 ---

28


![](content_assets/paper.pdf-0040-01.png)



![](content_assets/paper.pdf-0040-02.png)



![](content_assets/paper.pdf-0040-03.png)



![](content_assets/paper.pdf-0040-04.png)



![](content_assets/paper.pdf-0040-05.png)



![](content_assets/paper.pdf-0040-06.png)



![](content_assets/paper.pdf-0040-07.png)



![](content_assets/paper.pdf-0040-08.png)



![](content_assets/paper.pdf-0040-09.png)



![](content_assets/paper.pdf-0040-10.png)



![](content_assets/paper.pdf-0040-11.png)



![](content_assets/paper.pdf-0040-12.png)



![](content_assets/paper.pdf-0040-13.png)



![](content_assets/paper.pdf-0040-14.png)



![](content_assets/paper.pdf-0040-15.png)



![](content_assets/paper.pdf-0040-16.png)



![](content_assets/paper.pdf-0040-17.png)



![](content_assets/paper.pdf-0040-18.png)



![](content_assets/paper.pdf-0040-19.png)



![](content_assets/paper.pdf-0040-20.png)



![](content_assets/paper.pdf-0040-21.png)



![](content_assets/paper.pdf-0040-22.png)



![](content_assets/paper.pdf-0040-23.png)



![](content_assets/paper.pdf-0040-24.png)



![](content_assets/paper.pdf-0040-25.png)



![](content_assets/paper.pdf-0040-26.png)



![](content_assets/paper.pdf-0040-27.png)



![](content_assets/paper.pdf-0040-28.png)



![](content_assets/paper.pdf-0040-29.png)



![](content_assets/paper.pdf-0040-30.png)



![](content_assets/paper.pdf-0040-31.png)



![](content_assets/paper.pdf-0040-32.png)



![](content_assets/paper.pdf-0040-33.png)



![](content_assets/paper.pdf-0040-34.png)



![](content_assets/paper.pdf-0040-35.png)



![](content_assets/paper.pdf-0040-36.png)



![](content_assets/paper.pdf-0040-37.png)



![](content_assets/paper.pdf-0040-38.png)


Figure 1: Graph interpretation of the example zone and its closed form

As an example, consider the zone


![](content_assets/paper.pdf-0040-41.png)



![](content_assets/paper.pdf-0040-42.png)



![](content_assets/paper.pdf-0040-43.png)



![](content_assets/paper.pdf-0040-44.png)



![](content_assets/paper.pdf-0040-45.png)



![](content_assets/paper.pdf-0040-46.png)



![](content_assets/paper.pdf-0040-47.png)



![](content_assets/paper.pdf-0040-48.png)



![](content_assets/paper.pdf-0040-49.png)



![](content_assets/paper.pdf-0040-50.png)



![](content_assets/paper.pdf-0040-51.png)



![](content_assets/paper.pdf-0040-52.png)



![](content_assets/paper.pdf-0040-53.png)



![](content_assets/paper.pdf-0040-54.png)



![](content_assets/paper.pdf-0040-55.png)



![](content_assets/paper.pdf-0040-56.png)



![](content_assets/paper.pdf-0040-57.png)



![](content_assets/paper.pdf-0040-58.png)



![](content_assets/paper.pdf-0040-59.png)



![](content_assets/paper.pdf-0040-60.png)



![](content_assets/paper.pdf-0040-61.png)


. By combining the atomic constraints and we derive that , _i.e._ the bound on can be strengthened. Consider the graph interpretation of this zone, presented in Figure 1(a). The tighter bound on can be derived from the graph, using the path , giving the graph in Figure 1(b). Thus, deriving the tightest constraint on a pair of clocks in a zone is equivalent to finding the shortest path between their nodes in the graph interpretation of the zone. The conclusion is that a canonical, _i.e._ closed, version of a zone can be computed using a shortest path algorithm. Many verifiers for timed automata use the Floyd-Warshall algorithm [Flo62] (Algorithm 1) to transform zones to canonical form. However, since this algorithm is quite expensive (cubic in the number of clocks), it is desirable to make all frequently used operations preserve the canonical form, _i.e._ the result of performing an operation on a canonical zone should also be canonical.

**Algorithm 1** Floyds algorithm for computing shortest path

**for to do for to do for to do end for end for end for**


![](content_assets/paper.pdf-0040-65.png)



![](content_assets/paper.pdf-0040-66.png)



![](content_assets/paper.pdf-0040-67.png)



![](content_assets/paper.pdf-0040-68.png)



![](content_assets/paper.pdf-0040-69.png)



![](content_assets/paper.pdf-0040-70.png)


## **2.2 Minimal Constraint Systems**

A zone may contain redundant constraints. Obviously, it is desirable to remove such constraints to store only the minimal number of constraints. Consider,

--- end of page.page_number=40 ---

DBM: Structures, Operations and Implementation

29

for instance, the zone


![](content_assets/paper.pdf-0041-03.png)



![](content_assets/paper.pdf-0041-04.png)



![](content_assets/paper.pdf-0041-05.png)



![](content_assets/paper.pdf-0041-06.png)



![](content_assets/paper.pdf-0041-07.png)



![](content_assets/paper.pdf-0041-08.png)



![](content_assets/paper.pdf-0041-09.png)



![](content_assets/paper.pdf-0041-10.png)



![](content_assets/paper.pdf-0041-11.png)



![](content_assets/paper.pdf-0041-12.png)



![](content_assets/paper.pdf-0041-13.png)



![](content_assets/paper.pdf-0041-14.png)



![](content_assets/paper.pdf-0041-15.png)



![](content_assets/paper.pdf-0041-16.png)



![](content_assets/paper.pdf-0041-17.png)



![](content_assets/paper.pdf-0041-18.png)



![](content_assets/paper.pdf-0041-19.png)



![](content_assets/paper.pdf-0041-20.png)


, which is in minimal form. This zone is completely defined by only five constraints. However, the closed form contains no less than 12 constraints. It is known, _e.g._ from [LLPY97], that for each zone there is a minimal constraint system with the same solution set. By computing this minimal form for all zones and storing them in memory using a sparse representation we might reduce the memory consumption for state-space exploration. This problem has been thoroughly investigated in [LLPY97, Pet99, Lar00] and this presentation is a summary of the work presented there.

The goal is to find an algorithm that computes the minimal form of a closed DBM. However, closing a DBM corresponds to computing the shortest path between all clocks. Thus, we want to find an algorithm that computes the minimal set of bounds with a given shortest path closure. For clarity, the algorithm is presented in terms of directed weighted graphs. However, the results are directly applicable to the graph interpretation of DBMs.

First we introduce some notation: we say that a cycle in a graph is a _zero cycle_ if the sum of weights along the cycle is 0, and an edge is _redundant_ if there is another path between and where the sum of weights is no larger than .

In graphs without zero cycles we can remove all redundant edges without affecting the shortest path closure [Pet99]. Further, if the input graph is in shortest path form (as for closed DBMs) all redundant edges can be located by considering alternative paths of length two.

As an example, consider Figure 2. The figure shows the shortest path closure for a zero-cycle free graph (a) and its minimal form (b). In the graph we find that is made redundant by the path and can thus be removed. Further, the edge is redundant due to . Note that we consider edges marked as redundant when searching for new redundant edges. The reason is that we let the redundant edges represent the path making them redundant, thus allowing all redundant edges to be located using only alternative paths of length two. This procedure is repeated until no more redundant edges can be found.

This gives the procedure for removing redundant edges presented in Algorithm 2. The algorithm can be directly applied to zero-cycle free DBMs to compute the minimal number of constraints needed to represent a given zone.

--- end of page.page_number=41 ---

DBM: Structures, Operations and Implementation

30


![](content_assets/paper.pdf-0042-02.png)


Figure 2: A zero cycle free graph and its minimal form

**Algorithm 2** Reduction of Zero-Cycle Free Graph with nodes

**for to do for to do for to do if then** Mark edge as redundant **end if end for end for end for**

Remove all edges marked as redundant.

However, this algorithm will not work if there are zero-cycles in the graph. The reason is that the set of redundant edges in a graph with zero-cycles is not unique. As an example, consider the graph in Figure 3(a). Applying the above reasoning on this graph would remove based on the path . It would also remove the edge based on the path . But if both these edges are removed it is no longer possible to construct paths leading into . In this example there is a dependence between the edges and such that only one of them can be considered redundant.

The solution to this problem is to partition the nodes according to zero-cycles and build a super-graph where each node is a partition. The graph from Figure 3(a) has two partitions, one containing and and the other containing . To compute the edges in the super-graph we pick one representative for each partition and let the edges between the partitions inherit the weights from edges between the representatives. In our example, we choose and as

--- end of page.page_number=42 ---

DBM: Structures, Operations and Implementation

31


![](content_assets/paper.pdf-0043-02.png)



![](content_assets/paper.pdf-0043-03.png)



![](content_assets/paper.pdf-0043-04.png)


Figure 3: A graph with a zero-cycle and its minimal form

representatives for their equivalence classes. The edges in the graph are then and . The super-graph is clearly zero-cycle free and can be reduced using Algorithm 2. This small graph can not be reduced further. The relation between the nodes within a partition is uniquely defined by the zero-cycle and all other edges may be removed. In our example all edges within each equivalence class are part of the zero-cycle and thus none of them can be removed. Finally the reduced super-graph is connected to the reduced partitions. In our example we end up with the graph in Figure 3(b). Pseudo-code for the reduction-procedure is shown in Algorithm 3.

Now we have an algorithm for computing the minimum number of edges to represent a given shortest path closure that can be used to compute the minimum number of constraints needed to represent a given zone.

## **3 Operations on DBMs**

This section presents all operations on DBMs needed in symbolic state space exploration of timed automata, both for forwards and backwards analysis. Note that even if a verification tool only explores the state space in one direction all operations are still useful for other purposes, _e.g._ for generating diagnostic traces. The effects of the operations are shown graphically in Figure 5.

In the following section we do not distinguish between DBMs and zones, and the terms are used alternately. To simplify the presentation we assume that the clocks in are numbered and the index for is 0. We assume that the input zones are consistent and in canonical form.

--- end of page.page_number=43 ---

DBM: Structures, Operations and Implementation

32

**Algorithm 3** Reduction of negative-cycle free graph with nodes **for to do if** Node is not in a partition **then for to do if then** Node **end if end for end if end for** Let be a graph without nodes. **for each do** Pick one representative Node Add Node to Connect Node to all nodes in using weights from . **end for** Reduce **for each do** Add one zero cycle containing all nodes in to **end for**

The operations on DBMs can be divided into three different classes:

1. **Property-Checking:** Operations in this class include checking if a DBM is consistent, checking inclusion between zones, and checking whether a zone satisfies a given atomic constraint.

2. **Transformation:** This is the largest class containing operations for transforming zones according to guards, delay and reset.

3. **Normalisation:** They are used to normalise zones in order to obtain a finite zone-graph. In this paper we only describe one operation in this class, the so called -normalisation. For more normalisation operations we refer to [BY01].

--- end of page.page_number=44 ---

DBM: Structures, Operations and Implementation

33

## **3.1 Checking Properties of DBMs**

## **consistent( )**

The most basic operation on a DBM is to check if it is consistent, _i.e._ if the solution set is non-empty. In state-space exploration this operation is used to remove inconsistent states from exploration.

For a zone to be inconsistent there must be at least one pair of clocks where the upper bound on their difference is smaller than the lower bound. For DBMs this can be checked by searching for negative cost cycles in the graph interpretation. However, the most efficient way to implement a consistency check is to detect when an upper bound is set to lower value than the corresponding lower bound and mark the zone as inconsistent by setting to a negative value. For a zone in canonical form this test can be performed locally. To check if a zone is inconsistent it will then be enough to check whether is negative.

## **relation(**


![](content_assets/paper.pdf-0045-07.png)



![](content_assets/paper.pdf-0045-08.png)


## **)**

Another key operation in state space exploration is inclusion checking for the solution sets of two zones. For DBMs in canonical form, the condition that for all clocks is necessary and sufficient to conclude that . Naturally the opposite condition applies to checking if . This allows for the combined inclusion check described in Algorithm 5.

## **satisfied(**


![](content_assets/paper.pdf-0045-12.png)



![](content_assets/paper.pdf-0045-13.png)



![](content_assets/paper.pdf-0045-14.png)



![](content_assets/paper.pdf-0045-15.png)



![](content_assets/paper.pdf-0045-16.png)


## **)**


![](content_assets/paper.pdf-0045-18.png)


Sometimes it is desirable to non-destructively check if a zone satisfies a constraint, _i.e._ to check if the zone is consistent without altering . From the definition of the consistent-operation we know that a zone is consistent if it has no negative-cost cycles. Thus, checking if is non-empty can be done by checking if adding the guard to the zone would introduce a negative-cost cycle. For a DBM on canonical form this test can be performed locally by checking if is negative.

## **3.2 Transformations**

## **up( )**

The up operation computes the strongest post condition of a zone with respect to delay, _i.e._ up( ) contains the time assignments that can be reached from

--- end of page.page_number=45 ---

DBM: Structures, Operations and Implementation

34

by delay. Formally, this operation is defined as up .


![](content_assets/paper.pdf-0046-03.png)



![](content_assets/paper.pdf-0046-04.png)



![](content_assets/paper.pdf-0046-05.png)



![](content_assets/paper.pdf-0046-06.png)



![](content_assets/paper.pdf-0046-07.png)



![](content_assets/paper.pdf-0046-08.png)



![](content_assets/paper.pdf-0046-09.png)



![](content_assets/paper.pdf-0046-10.png)



![](content_assets/paper.pdf-0046-11.png)



![](content_assets/paper.pdf-0046-12.png)


Algorithmically, up is computed by removing the upper bounds on all individual clocks (In a DBM all elements are set to ). This is the same as saying that any time assignment in a given zone may delay an arbitrary amount of time. The property that all clocks proceed at the same speed is ensured by the fact that constraints on the differences between clocks are not altered by the operation.

This operation preserves the canonical form, _i.e._ applying up to a canonical DBM will result in a new canonical DBM. The reason is that to derive an upper bound on a single clock we need at least an upper bound on another clock and the relation between and , and all upper bounds have been removed by the operation. The up operation is also presented in Algorithm 6.

## **down( )**

This operation computes the weakest precondition of with respect to delay. Formally down , _i.e._ the set of time assignments that can reach by some delay . Algorithmically, down is computed by setting the lower bound on all individual clocks to . However due to constraints on clock differences this algorithm may produce non-canonical DBMs. As an example, consider the zone in Figure 4(a). When down is applied to this zone (Figure 4(b)), the lower bound on is and not , due to constraints on clock differences. Thus, to obtain an algorithm that produce canonical DBMs the difference constraints have to be taken into account when computing the new lower bounds.


![](content_assets/paper.pdf-0046-17.png)



![](content_assets/paper.pdf-0046-18.png)



![](content_assets/paper.pdf-0046-19.png)


Figure 4: Applying down to a zone.

To compute the lower bound for a clock , start by assuming that all other clocks have the value 0. Then examine all difference constraints and compute a new lower bound for under this assumption. The new bound on

--- end of page.page_number=46 ---

35

DBM: Structures, Operations and Implementation

will be the minimum bound on found in the DBM. Pseudo-code for down is presented in Algorithm 7.

## **and(**


![](content_assets/paper.pdf-0047-04.png)



![](content_assets/paper.pdf-0047-05.png)



![](content_assets/paper.pdf-0047-06.png)



![](content_assets/paper.pdf-0047-07.png)



![](content_assets/paper.pdf-0047-08.png)


## **)**


![](content_assets/paper.pdf-0047-10.png)


The most useful operation in state-space exploration is conjunction, _i.e._ adding a constraint to a zone. The basic step of the and operation is to check if and in this case set the bound to . If the bound has been altered, _i.e._ if adding the guard affected the solution set, the DBM has to be put back on canonical form. One way to do this would be to use the generic shortest path algorithm, however for this particular case it is possible to derive a specialisation of the algorithm allowing re-canonicalisation in instead of .

The specialised algorithm take advantage of the fact that is the only bound that has been changed. Since the Floyd-Warshall algorithm is insensitive to how the nodes in the graph are ordered, we may decide to treat and last. The outer loop of Algorithm 1 will then only affect the DBM twice, for and . This allows the canonicalisation algorithm to be reduced to checking, for all pairs of clocks in the DBM, if the path via either or is shorter than the direct connection. The pseudo code for this is presented in Algorithm 8.

## **free(**


![](content_assets/paper.pdf-0047-14.png)


## **)**


![](content_assets/paper.pdf-0047-16.png)


The free operation removes all constraints on a given clock, _i.e._ the clock may take any positive value. Formally this is expressed as free . In state-space exploration this operation is used in combination with conjunction, to implement reset operations on clocks. It can be used in both forwards and backwards exploration, but since forwards exploration allows other more efficient implementations of reset, free is only used when exploring the state-space backwards. A simple algorithm for this operation is to remove all bounds on in the DBM and set . However, the result may not be on canonical form. To obtain an algorithm preserving the canonical form, we change how new difference constraints regarding are derived. We note that the constraint can be combined with constraints of the form to compute new bounds for . For instance, if we can derive that . To obtain a DBM on canonical form we derive bounds for based on instead of setting .In Algorithm 9 this is presented as pseudo code.

--- end of page.page_number=47 ---

DBM: Structures, Operations and Implementation

36

## **reset(**


![](content_assets/paper.pdf-0048-03.png)



![](content_assets/paper.pdf-0048-04.png)


## **)**


![](content_assets/paper.pdf-0048-06.png)


In forwards exploration this operation is used to set clocks to specific values, _i.e._ reset . Without the requirement that output should be on canonical form, reset can be implemented by setting , and remove all other bounds on . However, if we instead of removing the difference constraints compute new values using constraints on the other clocks, like in the implementation of free, we obtain an implementation that preserve the canonical form. Such an implementation is presented in Algorithm 10.

## **copy(**


![](content_assets/paper.pdf-0048-09.png)



![](content_assets/paper.pdf-0048-10.png)


## **)**


![](content_assets/paper.pdf-0048-12.png)


This is another operation used in forwards state-space exploration. It copies the value of one clock to another. Formally, we define reset as . Analogous with reset, copy can be implemented by assigning , , removing all other bounds on and re-canonicalise the zone. However, a more efficient implementation is obtained by assigning , and then copy the rest of the bounds on from . For pseudo code, see Algorithm 11

## **shift(**


![](content_assets/paper.pdf-0048-15.png)



![](content_assets/paper.pdf-0048-16.png)



![](content_assets/paper.pdf-0048-17.png)



![](content_assets/paper.pdf-0048-18.png)


## **)**


![](content_assets/paper.pdf-0048-20.png)


The last reset operation is shifting a clock, _i.e._ adding or subtracting a clock with an integer value, _i.e._ shift . The definition gives a hint on how to implement the operation. We can view the shift operation as a substitution of for in the zone. With this reasoning is added to the upper and lower bounds of . However, since lower bounds on are represented by constraints on , is subtracted from all those bounds. This operation is presented in pseudo-code in Algorithm 12

## **3.3 Normalisation Operations**

## **norm (**


![](content_assets/paper.pdf-0048-24.png)



![](content_assets/paper.pdf-0048-25.png)



![](content_assets/paper.pdf-0048-26.png)



![](content_assets/paper.pdf-0048-27.png)



![](content_assets/paper.pdf-0048-28.png)



![](content_assets/paper.pdf-0048-29.png)


## **)**

To obtain a finite zone graph most verifiers use some kind of normalisation of - zones. One of the key steps in most normalisation algorithms is the so called normalisation, _i.e._ the zone is normalised with respect to the maximum constant each clock is compared to in the automaton.

--- end of page.page_number=48 ---

DBM: Structures, Operations and Implementation

37

The procedure to obtain the -normalisation of a given zone is to remove all bounds such that and to set all bounds such that to . This corresponds to removing all upper bounds higher than the maximum constant and lowering all lower bounds higher than the maximum constant down to the maximum constant.

The -normalisation operation will not preserve the canonical form of the DBM, and in this case the best way to put the result back on canonical form is to use Algorithm 1. Pseudo-code for -normalisation is given in Algorithm 13


![](content_assets/paper.pdf-0049-04.png)


Figure 5: All DBM operations applied to the same zone

--- end of page.page_number=49 ---

DBM: Structures, Operations and Implementation

38

## **4 Zones in Memory**

This section describes a number of techniques for storing zones in computer memory. The section starts by describing how to map DBM elements on machine words. It continues by discussing how to place two-dimensional DBMs in one-dimensional memory and ends by describing how to store zones using a sparse representation.

## **4.1 Storing DBM Elements**

To store a DBM element in memory we need to keep track of the integer limit and whether it is strict or not. The range of the integer limit is typically much lower than the maximum value of a machine word and the strictness can be stored using just one bit. Thus, it is possible to store both the limit and the strictness in different parts of the same machine word. Since comparing and adding DBM elements are frequently used operations it is crucial for the performance of a DBM package that they can be efficiently implemented for the chosen encoding. Fortunately, it is possible to construct an encoding of bounds in machine words, where checking if is less than can be performed by checking if the encoded is smaller than the encoded .

The encoding we propose is to use the least significant bit (LSB) of the machine word to store whether the bound is strict or not. Since strict bounds are smaller than non-strict we let a set (1) bit denote that the bound is non-strict while an unset (0) bit denote that the bound is strict. The rest of the bits in the machine word are used to store the integer bound. To encode we use the largest positive number that fit in a machine word (denoted MAX_INT).

For good performance we also need an efficient implementation of addition of bounds. For the proposed encoding Algorithm 4 adds two encoded bounds and . The symbols and in the algorithm are used to denote bitwise-and and bitwise-or, respectively.

**Algorithm 4** Algorithm for adding encoded bounds

**if** MAX_INT or MAX_INT **then return** MAX_INT **else return end if**

--- end of page.page_number=50 ---

DBM: Structures, Operations and Implementation

39

## **4.2 Placing DBMs in Memory**

Another implementation issue is how to store two-dimensional DBMs in linear memory. In this section we present two different techniques and give a brief comparison between them. The natural way to put matrices in linear memory is to store the elements by row (or by column), _i.e._ each row of the matrix is stored consequently in memory. This layout has one big advantage, its good performance. This advantage is mainly due to the simple function for computing the location of a given element in the matrix: . This function can (on most computers) be computed in only two instructions. This is important since all accesses to DBM elements use this function. How the different DBM elements are place in memory with this layout if presented in Figure 6(a).

The second way to store a DBM in linear memory is based on a layered model where each layer consists of the bounds between a clock and the clocks with lower index in the DBM. In this representation it is cheap to implement local clocks, since all information about the local clocks are localised at the end of the DBM. The drawback with this layout is the more complicated function from DBM indices to memory locations. For this layout we have:


![](content_assets/paper.pdf-0051-05.png)



![](content_assets/paper.pdf-0051-06.png)



![](content_assets/paper.pdf-0051-07.png)



![](content_assets/paper.pdf-0051-08.png)



![](content_assets/paper.pdf-0051-09.png)



![](content_assets/paper.pdf-0051-10.png)



![](content_assets/paper.pdf-0051-11.png)



![](content_assets/paper.pdf-0051-12.png)



![](content_assets/paper.pdf-0051-13.png)



![](content_assets/paper.pdf-0051-14.png)



![](content_assets/paper.pdf-0051-15.png)



![](content_assets/paper.pdf-0051-16.png)



![](content_assets/paper.pdf-0051-17.png)



![](content_assets/paper.pdf-0051-18.png)



![](content_assets/paper.pdf-0051-19.png)



![](content_assets/paper.pdf-0051-20.png)



![](content_assets/paper.pdf-0051-21.png)



![](content_assets/paper.pdf-0051-22.png)


This adds at least two instructions (one comparison and one conditional jump) to the transformation. This may not seem such a huge overhead, but it is clearly noticeable. The cache performance is also worse when using this layout than when storing the DBMs row-wise. This layout is illustrated in Figure 6(b).

The conclusion is that unless the tool under construction supports adding and removing clocks dynamically the row-wise mapping should be used. On the other hand, if the tool supports local clocks the layered mapping may be preferable since no reordering of the DBM is needed when entering or leaving a clock scope.

## **4.3 Storing Sparse Zones**

In most verification tools, the majority of the zones are kept in the set of states already visited during verification. They are used as a reference to ensure termination by preventing states from being explored more than once. For the states

--- end of page.page_number=51 ---

DBM: Structures, Operations and Implementation

40


![](content_assets/paper.pdf-0052-02.png)



![](content_assets/paper.pdf-0052-03.png)



![](content_assets/paper.pdf-0052-04.png)



![](content_assets/paper.pdf-0052-05.png)



![](content_assets/paper.pdf-0052-06.png)



![](content_assets/paper.pdf-0052-07.png)



![](content_assets/paper.pdf-0052-08.png)



![](content_assets/paper.pdf-0052-09.png)



![](content_assets/paper.pdf-0052-10.png)



![](content_assets/paper.pdf-0052-11.png)



![](content_assets/paper.pdf-0052-12.png)



![](content_assets/paper.pdf-0052-13.png)



![](content_assets/paper.pdf-0052-14.png)



![](content_assets/paper.pdf-0052-15.png)



![](content_assets/paper.pdf-0052-16.png)



![](content_assets/paper.pdf-0052-17.png)



![](content_assets/paper.pdf-0052-18.png)



![](content_assets/paper.pdf-0052-19.png)



![](content_assets/paper.pdf-0052-20.png)



![](content_assets/paper.pdf-0052-21.png)



![](content_assets/paper.pdf-0052-22.png)



![](content_assets/paper.pdf-0052-23.png)



![](content_assets/paper.pdf-0052-24.png)



![](content_assets/paper.pdf-0052-25.png)



![](content_assets/paper.pdf-0052-26.png)



![](content_assets/paper.pdf-0052-27.png)



![](content_assets/paper.pdf-0052-28.png)



![](content_assets/paper.pdf-0052-29.png)



![](content_assets/paper.pdf-0052-30.png)



![](content_assets/paper.pdf-0052-31.png)



![](content_assets/paper.pdf-0052-32.png)



![](content_assets/paper.pdf-0052-33.png)



![](content_assets/paper.pdf-0052-34.png)



![](content_assets/paper.pdf-0052-35.png)



![](content_assets/paper.pdf-0052-36.png)



![](content_assets/paper.pdf-0052-37.png)



![](content_assets/paper.pdf-0052-38.png)



![](content_assets/paper.pdf-0052-39.png)



![](content_assets/paper.pdf-0052-40.png)



![](content_assets/paper.pdf-0052-41.png)



![](content_assets/paper.pdf-0052-42.png)



![](content_assets/paper.pdf-0052-43.png)



![](content_assets/paper.pdf-0052-44.png)



![](content_assets/paper.pdf-0052-45.png)



![](content_assets/paper.pdf-0052-46.png)



![](content_assets/paper.pdf-0052-47.png)



![](content_assets/paper.pdf-0052-48.png)



![](content_assets/paper.pdf-0052-49.png)



![](content_assets/paper.pdf-0052-50.png)



![](content_assets/paper.pdf-0052-51.png)



![](content_assets/paper.pdf-0052-52.png)



![](content_assets/paper.pdf-0052-53.png)



![](content_assets/paper.pdf-0052-54.png)


Figure 6: Different layouts of DBMs in memory

in this set we may benefit from storing only the minimal number of constraints using a sparse representation.

A straight forward implementation is to store a sparse zone as a vector of constraints of the form . We may save additional memory by omitting implicit constraints, such as . A downside with using sparse zones is that each constraint require twice the amount of memory needed for a constraint in a full DBM, since the sparse representation must store clock indices explicitly. Thus, unless half of the constraints in a DBM are redundant we do not gain from using sparse zones.

A good feature of the sparse representation is that checking whether a zone represented as a full DBM is included in a sparse zone may be implemented without computing the full DBM for . It suffices to check for all constraints in that the corresponding bound in is tighter. However, to check if we have to compute the full DBM for .

## **5 Conclusions**

In this paper we have reviewed Difference Bound Matrices as a data-structure for timing constraints. We have presented the basics of the data-structure and all operations needed in symbolic state-space exploration of timed automata. We have also discussed how to save space by computing the minimum number of constraints defining a given zone and saving them using a sparse representation.

## **References**

- [ABB 01] Tobias Amnell, Gerd Behrmann, Johan Bengtsson, Pedro R. D’Argenio, Alexandre David, Ansgar Fehnker, Thomas Hune, Bertrand Jeannet, Kim G. Larsen, M. Oliver Möller, Paul Pettersson, Carsten Weise, and Wang Yi. UPPAAL - Now, Next, and Future. In _Modelling and Verification_

--- end of page.page_number=52 ---

DBM: Structures, Operations and Implementation

41

_of Parallel Processes_ , volume 2067 of _Lecture Notes in Computer Science_ , pages 100–125. Springer-Verlag, 2001.

- [AD90] Rajeev Alur and David L. Dill. Automata for modeling real-time systems. In _Proceedings, Seventeenth International Colloquium on Automata, Languages and Programming_ , volume 443 of _Lecture Notes in Computer Science_ , pages 322–335. Springer-Verlag, 1990.

- [AD94] Rajeev Alur and David L. Dill. A theory of timed automata. _Journal of Theoretical Computer Science_ , 126(2):183–235, 1994.

- [BL96] Johan Bengtsson and Fredrik Larsson. UPPAAL a tool for automatic verification of real-time systems. Technical Report 96/67, Department of Computer Systems, Uppsala University, 1996.

- [BY01] Johan Bentsson and Wang Yi. Reachability analysis of timed automata containing constraints on clock differences. Submitted for publication., 2001.

- [Dil89] David L. Dill. Timing assumptions and verification of finite-state concurrent systems. In _Proceedings, Automatic Verification Methods for Finite State Systems_ , volume 407 of _Lecture Notes in Computer Science_ , pages 197–212. Springer-Verlag, 1989.

- [DOTY95] Conrado Daws, Alfredo Olivero, Stavros Tripakis, and Sergio Yovine. The tool Kronos. In _Proceedings, Hybrid Systems III: Verification and Control_ , volume 1066 of _Lecture Notes in Computer Science_ . Springer-Verlag, 1995.

- [Flo62] Robert W. Floyd. Acm algorithm 97: Shortest path. _Communications of the ACM_ , 5(6):345, June 1962.

- [Lar00] Fredrik Larsson. Efficient implementation of model-checkers for networks of timed automata. Licentiate Thesis 2000-003, Department of Information Technology, Uppsala University, 2000.

- [LLPY97] Kim G. Larsen, Fredrik Larsson, Paul Pettersson, and Wang Yi. Efficient verification of real-time systems: Compact data structure and state space reduction. In _Proceedings, 18_ th _IEEE Real-Time Systems Symposium_ , pages 14–24. IEEE Computer Society Press, 1997.

- [LPY97] Kim G. Larsen, Paul Petterson, and Wang Yi. UPPAAL in a nutshell. _Journal on Software Tools for Technology Transfer_ , 1997.

- [Pet99] Paul Pettersson. _Modelling and Verification of Real-Time Systems Using Timed Automata: Theory and Practice_ . PhD thesis, Uppsala University, 1999.

- [Yov97] Sergio Yovine. Kronos: a verification tool for real-time systems. _Journal on Software Tools for Technology Transfer_ , 1, October 1997.

--- end of page.page_number=53 ---

DBM: Structures, Operations and Implementation

42

## **A Pseudo-Code**

**Algorithm 5** relation( ) tt tt **for to do for to do end for end for return**


![](content_assets/paper.pdf-0054-04.png)



![](content_assets/paper.pdf-0054-05.png)



![](content_assets/paper.pdf-0054-06.png)



![](content_assets/paper.pdf-0054-07.png)



![](content_assets/paper.pdf-0054-08.png)



![](content_assets/paper.pdf-0054-09.png)


**Algorithm 6** up( ) **for to do end for**

**Algorithm 7** down( ) **for to do for to do if then end if end for end for**

--- end of page.page_number=54 ---

DBM: Structures, Operations and Implementation

43

**Algorithm 8** and( ) **if then else if then for to do for** to **do if then end if if then end if end for end for end if**

**Algorithm 9** free( )

**for to do if then end if end for**

**Algorithm 10** reset(


![](content_assets/paper.pdf-0055-06.png)



![](content_assets/paper.pdf-0055-07.png)



![](content_assets/paper.pdf-0055-08.png)


**for to do end for**


![](content_assets/paper.pdf-0055-10.png)



![](content_assets/paper.pdf-0055-11.png)



![](content_assets/paper.pdf-0055-12.png)



![](content_assets/paper.pdf-0055-13.png)



![](content_assets/paper.pdf-0055-14.png)


--- end of page.page_number=55 ---

DBM: Structures, Operations and Implementation

44

**Algorithm 11** copy( ) **for to do if then end if end for**


![](content_assets/paper.pdf-0056-03.png)



![](content_assets/paper.pdf-0056-04.png)



![](content_assets/paper.pdf-0056-05.png)



![](content_assets/paper.pdf-0056-06.png)



![](content_assets/paper.pdf-0056-07.png)



![](content_assets/paper.pdf-0056-08.png)



![](content_assets/paper.pdf-0056-09.png)



![](content_assets/paper.pdf-0056-10.png)



![](content_assets/paper.pdf-0056-11.png)



![](content_assets/paper.pdf-0056-12.png)


**Algorithm 12** shift( ) **for to do if then end if end for**


![](content_assets/paper.pdf-0056-14.png)



![](content_assets/paper.pdf-0056-15.png)



![](content_assets/paper.pdf-0056-16.png)



![](content_assets/paper.pdf-0056-17.png)



![](content_assets/paper.pdf-0056-18.png)



![](content_assets/paper.pdf-0056-19.png)



![](content_assets/paper.pdf-0056-20.png)



![](content_assets/paper.pdf-0056-21.png)



![](content_assets/paper.pdf-0056-22.png)



![](content_assets/paper.pdf-0056-23.png)



![](content_assets/paper.pdf-0056-24.png)



![](content_assets/paper.pdf-0056-25.png)



![](content_assets/paper.pdf-0056-26.png)



![](content_assets/paper.pdf-0056-27.png)



![](content_assets/paper.pdf-0056-28.png)



![](content_assets/paper.pdf-0056-29.png)



![](content_assets/paper.pdf-0056-30.png)



![](content_assets/paper.pdf-0056-31.png)



![](content_assets/paper.pdf-0056-32.png)



![](content_assets/paper.pdf-0056-33.png)



![](content_assets/paper.pdf-0056-34.png)


**Algorithm 13** norm ( ) **for** to **do for** to **do if** and **then else if** and **then end if end for end for** close( )

--- end of page.page_number=56 ---

## **Paper B:**

**Reachability Analysis of Timed Automata Containing Constraints on Clock Differences**

Johan Bengtsson and Wang Yi.

--- end of page.page_number=57 ---

--- end of page.page_number=58 ---

Timed Automata with Constraints on Clock Differences

47

## **Reachability Analysis of Timed Automata Containing Constraints on Clock Differences**

## Johan Bengtsson and Wang Yi

Department of Computer Systems, Uppsala University, Sweden. E-mail: {johanb,yi}@docs.uu.se

**Abstract.** The key step to guarantee termination of reachability analysis for timed automata is the normalisation algorithms for clock constraints (i.e. symbolic states represented as DBM’s). It transforms DBM’s which may contain arbitrary constants into their equivalent according to maximal constants appearing in clock constraints of an automaton. A restriction of the existing algorithms is that clock constraints in timed automata must be in the form [AD94] of where is a clock, , and is a natural number. It was discovered recently that the existing tools were either providing incorrect answers or not terminating when they are used to verify automata containing difference constraints of the form: (that are indeed needed in many applications e.g. in solving scheduling problems). In this paper, we present new normalisation algorithms that transforms DBM’s according to not only maximal constants of clocks but also difference constraints appearing in an automata. To our knowledge, they are the first published normalisation algorithms for timed automata containing difference constraints. The algorithms have been implemented in UPPAAL, demonstrating that little extra overhead is needed to deal with difference constraints.

## **1 Introduction**

Following the work of Alur and Dill on timed automata [AD94], a number of model checkers have been developed for modelling and verification of timed systems with timed automata as the core of their input languages [DOTY95, Yov97, LPY97, ABB 01] based on reachability analysis. The foundation for decidability of reachability problems for timed automata is Alur and Dill’s region technique, by which the infinite state space of a timed automaton due to the density of time, may be partitioned into finitely many equivalence classes i.e. according to regions in such a way that states within each class will always evolve to states within the same classes. However, analysis based on the region technique is practically infeasible due to the large number of equivalence

--- end of page.page_number=59 ---

Timed Automata with Constraints on Clock Differences

48

classes [LPY95], which is highly exponential in the number of clocks and their maximal constants.

One of the major advances in the area after the pioneering work of Alur and Dill is the symbolic technique [Dil89, YL93, HNSY94, YPD94, LPY95], which transforms the reachability problem to that of solving simple constraints. It adopts the idea from symbolic model checking for untimed systems, which uses logical formulas to represent set of states and operations on formulas to represent state transitions. It is proven that the infinite state-space of timed automata can be finitely partitioned into symbolic states which are represented and manipulated using a class of linear constraints known as zones and represented as _Difference Bound Matrices_ (DBM) [Bel57, Dil89]. The reachability relation over symbolic states can be represented and computed by a few efficient operations on zones. From now on, we shall not distinguish the terms: constraint, zone and DBM.

The technique can be simply formulated in an abstract reachability algorithm[1] as shown in Algorithm 1. The algorithm is to check whether a timed automaton may reach a final location . It explores the state space of the automaton in terms of symbolic states in the form where is a location and is a zone (represented as a DBM).

**Algorithm 1** Symbolic reachability analysis

PASSED WAIT **while** WAIT **do** take from WAIT **if then return** “YES” **if** for all PASSED **then** add to PASSED **for all** such that **do** add to WAIT **end for end if end while return** “NO”

Having a closer look at the algorithm, one will realize that termination is not guaranteed unless the number of constraints generated is finite or the constraints

> 1 Several verification tools for timed systems (e.g. UPPAAL [BLL 96]) have been implemented based on this algorithm.

--- end of page.page_number=60 ---

Timed Automata with Constraints on Clock Differences

49

form a well quasi-ordering with respects to set-inclusion (over solution sets for clock constraints) [Hig52]. There have been several normalisation algorithms for clock constraints represented as DBMs (e.g. [Rok93, Pet99]) that are the key step to guarantee termination for the existing tools. They transform DBMs which may contain arbitrary constants into their equivalent with maximal constants appearing in clock constraints. The transformation respects region equivalence and therefore the number of DBMs explored is finite. However a restriction of the existing normalisation algorithms is that clock constraints in the syntax of timed automata must be in the form [AD94] of where is a clock variable, is a relational operator and is a natural number. It was discovered recently that the existing tools were either providing incorrect answers or not terminating when they are used to verify automata containing difference constraints of the form: (that are indeed needed in many applications e.g. in solving scheduling problems).

A normalisation algorithm based on region equivalence treats clock values above a certain constant as equivalent. This is correct only when no guard of the form: is allowed in an automaton. Otherwise the normalisation operation may enlarge a zone so that the guard (a difference constraint) labelled on a transition is made true and thus incorrectly enables the transition. For automata containing difference constraints as guards, we need a finer partitioning, since the difference constraints introduce diagonal lines that split the entire clock space, even above the maximum constants for clocks. The partitioning and related normalisation operation based on region construction is too crude.

We demonstrate this by an example. Consider the example shown in Figure 1. The final location of the automaton is not reachable according to the semantics. This is because in location , the clock zone is ( and ) where the guard is ( and ) which is equivalent to ( and and ) can never be true and thus disables the last transition. However, because the maximal constants for clock is (and for ), the zone in location : ( and ) will be normalised to ( and ) by the maximal constant for , which enables the guard ( and ) leading to the final location. Thus the symbolic reachability analysis based on a standard normalisation algorithm would incorrectly conclude that the last location is reachable.

In [BDGP98], it has been proved that a timed automaton with constraints on clock differences can be transformed to an equivalent automaton without constraints on differences. However, this approach is impractical to be implemented in the existing tools that support debugging of models because the transfor-

--- end of page.page_number=61 ---

50

Timed Automata with Constraints on Clock Differences


![](content_assets/paper.pdf-0062-02.png)


Figure 1: Bug example

mation will change the syntax of the original automaton. In this paper, we present two normalisation algorithms that allow not only clock comparison with naturals but also comparison between clocks i.e. constraints on clock differences. The algorithms transform DBMs according to not only the maximal constants of clocks but also difference constraints appearing in an automaton. To our knowledge, they are the first published normalisation algorithms for timed automata containing difference constraints. The algorithms have been implemented in UPPAAL. Our experiments demonstrate that almost no extra overhead is added to deal with difference constraints.

The paper is organised as follows: Section 2 reviews timed automata and reachability analysis. Section 3 introduces the problem in normalising symbolic states for timed automata with constraints over clock differences. Section 4 presents two new normalisation algorithms. Section 5 concludes the paper.

## **2 Preliminaries**

In this section we briefly review the notation for timed automata and its semantics. More extensive descriptions can be found in _e.g._ [AD94, Yov98, Pet99].

## **2.1 Timed Automata Model**

Let be a finite set of labels, ranged over by etc. A timed automaton is a finite state automaton over alphabet extended with a set of real valued clocks, to model time dependent behaviour. Let denote a set of clocks, ranged over by , and define as the set of conjunctions of atomic constraints of the form and for and . We use for the subset of where all atomic constraints are of the form and let range over this set.

--- end of page.page_number=62 ---

51

Timed Automata with Constraints on Clock Differences

**Definition 1 (Timed Automaton)** _A timed automaton is a tuple where is a set of control nodes, is the initial node, is the set of edges and assign invariants to locations. As a simplification we will use to denote ._ The clocks values are formally represented as functions, called clock assignments, mapping to the non-negative reals . We let denote such functions, and use to denote that the clock assignment satisfy the formula . For we use for the clock assignment that map all clocks in to the value , and for we let denote the clock assignment that map all clocks, , in the domain of to and agree with for the other clocks in

The semantics of a timed automaton is a timed transition-system where the states are pairs , with two types of transitions, corresponding to delay transitions and discrete action transitions respectively:


![](content_assets/paper.pdf-0063-04.png)



![](content_assets/paper.pdf-0063-05.png)



![](content_assets/paper.pdf-0063-06.png)



![](content_assets/paper.pdf-0063-07.png)



![](content_assets/paper.pdf-0063-08.png)



![](content_assets/paper.pdf-0063-09.png)



![](content_assets/paper.pdf-0063-10.png)



![](content_assets/paper.pdf-0063-11.png)



![](content_assets/paper.pdf-0063-12.png)


if and


![](content_assets/paper.pdf-0063-14.png)



![](content_assets/paper.pdf-0063-15.png)



![](content_assets/paper.pdf-0063-16.png)



![](content_assets/paper.pdf-0063-17.png)



![](content_assets/paper.pdf-0063-18.png)



![](content_assets/paper.pdf-0063-19.png)



![](content_assets/paper.pdf-0063-20.png)


if and


![](content_assets/paper.pdf-0063-22.png)



![](content_assets/paper.pdf-0063-23.png)



![](content_assets/paper.pdf-0063-24.png)


It is easy to see that the state space for such a transition system is infinite and thus not adequate for algorithmic verification. However, efficient algorithms may be obtained using a _symbolic semantics_ based on _symbolic states_ of the form , where [HNSY92, YPD94]. The symbolic counterpart of the transitions are given by:


![](content_assets/paper.pdf-0063-26.png)



![](content_assets/paper.pdf-0063-27.png)



![](content_assets/paper.pdf-0063-28.png)



![](content_assets/paper.pdf-0063-29.png)



![](content_assets/paper.pdf-0063-30.png)



![](content_assets/paper.pdf-0063-31.png)



![](content_assets/paper.pdf-0063-32.png)



![](content_assets/paper.pdf-0063-33.png)



![](content_assets/paper.pdf-0063-34.png)



![](content_assets/paper.pdf-0063-35.png)



![](content_assets/paper.pdf-0063-36.png)



![](content_assets/paper.pdf-0063-37.png)



![](content_assets/paper.pdf-0063-38.png)



![](content_assets/paper.pdf-0063-39.png)



![](content_assets/paper.pdf-0063-40.png)



![](content_assets/paper.pdf-0063-41.png)



![](content_assets/paper.pdf-0063-42.png)



![](content_assets/paper.pdf-0063-43.png)


## if


![](content_assets/paper.pdf-0063-45.png)



![](content_assets/paper.pdf-0063-46.png)



![](content_assets/paper.pdf-0063-47.png)



![](content_assets/paper.pdf-0063-48.png)


where and . It can be shown that the set of constraint systems is closed under these operations, in the sense that the result of the operations can be expressed by elements of .

Moreover the symbolic semantics correspond closely to the standard semantics in the sense that if then, for all there is such that .

## **2.2 Reachability Analysis**

Given a timed automaton with symbolic initial-state and a symbolic state , is said to be _reachable_ if and

--- end of page.page_number=63 ---

52

Timed Automata with Constraints on Clock Differences

for some . This problem may be solved using a standard reachability algorithm for graphs. However the unbounded clock values may render an infinite zone graph and thus might the reachability algorithm not terminate. The solution to this problem is to obtain a finite symbolic semantics by normalising the states with respect to the maximum constant each clock is compared to in the automaton. For details we refer the reader to [Pet99, Rok93] but the main fact and the intuition behind it is described here. In order to do this we first have to introduce the notion of closed constraint systems. We say that a constraint system is _closed under entailment_ or just closed, for short, if no constraint in can be strengthened without reducing the solution set.

**Proposition 1** _For each constraint system there is a unique constraint system such that and have exactly the same solution set and is closed under entailment._

From this proposition we conclude that a closed constraint system can be used as a canonical representation of a zone.

Given a zone and a set of maximal constants where denotes the maximal constant for clock , the normalisation of , denoted norm , is computed from the closed representation of by

1. Removing all constraints of the form , , and where ,

2. Replacing all constraints of the form , , and where with and respectively.

This can then be used to define a notion of normalised symbolic transitions ( ) by modifying the transitions of the standard symbolic semantics to preserve normalisation. The discrete action transition already preserves this so there is no need to modify it, but the delay transition should be modified to norm .

**Proposition 2** _Assume a timed automaton with initial-state and let be the set of maximal constants used to compare with respective clocks in . Then is reachable from if and only if there is a sequence of normalised transitions such that ._

Using this we get a finite symbolic state-space where we can apply a standard reachability algorithm for graphs, such as the one in Algorithm 1 with the symbolic transition relation being replaced with the normalised version .

--- end of page.page_number=64 ---

53

Timed Automata with Constraints on Clock Differences

## **3 Constraints on Clock Differences and Normalisation**

Timed automata can easily be extended to allow guards where the difference between two clocks is compared, _i.e._ allowing the guards to be taken from the full set , not only from . However, this extension do not give more expressive power; it has been shown ( _e.g._ in [BDGP98]) that a timed automaton with difference constraints can be transformed into an equivalent automaton without difference constraints. From now on, we will call the timed automata described in Section 2 for _diagonal free timed automata_ and widen the term timed automata to include also automata with difference constraints.

We note that for diagonal-free timed automata the normalisation algorithm described earlier is based on the so called region equivalence.

**Definition 2 (Region Equivalence)** _For a clock , let be a constant (the ceiling of clock ). For a real number , let denote the fractional part of , and denote its integer part. Two clock assignments are_ regionequivalent _, denoted , iff_

_1. for each clock , either or and , and_

_2. for all clocks if and then_

   - _(a) iff and_

   - _(b) iff_


![](content_assets/paper.pdf-0065-10.png)



![](content_assets/paper.pdf-0065-11.png)



![](content_assets/paper.pdf-0065-12.png)



![](content_assets/paper.pdf-0065-13.png)



![](content_assets/paper.pdf-0065-14.png)



![](content_assets/paper.pdf-0065-15.png)



![](content_assets/paper.pdf-0065-16.png)



![](content_assets/paper.pdf-0065-17.png)



![](content_assets/paper.pdf-0065-18.png)


For the extended version we need a finer partitioning, since the difference constraints in the guards introduce diagonal lines that split the entire clock space, even above the maximum constants for the clocks. The partitioning used for diagonal-free automata, and the connected normalisation operation norm is too crude. We demonstrate this by an example: Consider the timed automaton in Figure 2. The automaton has two clocks, (with maximum constant 0) and (with maximum constant 1). The only difference constraint in the example is . This will be used as a running example throughout the paper since the small number of clocks make it possible to show the zones using graphs.

The problem is easily detected by comparing the clock zones of the unnormalised symbolic semantics (presented in Figure 3) with the corresponding clock zones in the normalised symbolic semantics (presented in Figure 4). To highlight the cause of the problem even further we show borders between equivalence classes in the clock space ( from the maximum constant for and

--- end of page.page_number=65 ---

54

Timed Automata with Constraints on Clock Differences


![](content_assets/paper.pdf-0066-02.png)


Figure 2: Example automaton with difference guards

from the difference constraint) as dashed lines. The initial state of the automaton is After performing the first action step it will reach the state . Idling in location leads to the state . Since this is above the maximum constant of the corresponding state in the normalised semantics will be . Thus, the normalised state will, erroneously, contain time assignments from the triangle even though no state in the real semantics has a time assignment in this equivalence class. Performing the next action step will take the automaton to the state . The next step in the normalised semantics is the state . The automaton may now idle to the state . The corresponding state in the normalised semantics is . In the real semantics no further step is possible since the guard is not satisfied while the normalised semantics may proceed to location since the time assignments satisfying are present in the normalised states. The conclusion is that the normalisation procedure have to be adapted to handle timed automata with difference constraints.

## **4 New Normalisation Algorithms**

In this section we will present how to normalise the symbolic states for a timed automaton with difference constraints together with two slightly different algorithms to do this. The first algorithm is simpler, and may still yield an infinite zone graph. However, the zones form a well quasi-order with respect to inclusion checking and thus the reachability algorithm is guaranteed to terminate (see _e.g._ [ACJT00]). The second algorithm is more complex and does not suf-[ˇ] fer from this problem, but it may require splitting of symbolic states.

--- end of page.page_number=66 ---

55

Timed Automata with Constraints on Clock Differences


![](content_assets/paper.pdf-0067-02.png)



![](content_assets/paper.pdf-0067-03.png)


Leaving S0


![](content_assets/paper.pdf-0067-05.png)



![](content_assets/paper.pdf-0067-06.png)



![](content_assets/paper.pdf-0067-07.png)


Entering S1 Leaving S1


![](content_assets/paper.pdf-0067-09.png)



![](content_assets/paper.pdf-0067-10.png)



![](content_assets/paper.pdf-0067-11.png)



![](content_assets/paper.pdf-0067-12.png)


Entering S2 Leaving S2 Entering S3

Figure 3: Zones for the example automaton, without normalisation


![](content_assets/paper.pdf-0067-15.png)



![](content_assets/paper.pdf-0067-16.png)



![](content_assets/paper.pdf-0067-17.png)



![](content_assets/paper.pdf-0067-18.png)


Figure 4: Zones for the example automaton, with incorrect normalisation

--- end of page.page_number=67 ---

56

Timed Automata with Constraints on Clock Differences

## **4.1 Region Equivalence Refined by Difference Constraints**

The key issue for the extended normalisation algorithms is to honour the equivalence classes that are introduced by difference constraints in the guards. We note that difference constraints in the guards may introduce equivalence classes in the clock space that reach beyond any maximum constant. Thus we need to refine the region equivalence from Definition 2 to take the difference constraints into account.

**Definition 3 (Refined Region Equivalence)** _Let be a finite set of constraints of the form for , and . Two clock assignments are equivalent, iff and_

We note that since the number of regions defined by is finite and there are only finitely many constraints in this refined region equivalence will define finitely many regions.

## **4.2 The Core of Normalisation**

We can now use the refined region equivalence from Definition 3 to obtain the core of a normalisation algorithm. From the region equivalence we get the need to ensure that if a difference constraint is not satisfied by any point in the unnormalised zone, , then it should not be satisfied by any point in the normalised zone, norm , and if all points in satisfy a difference constraint then so should all points in norm . This leads to a core normalisation algorithm consisting of three stages:

1. Collect all difference constraints from that are not satisfied by any point in the zone and the negation of all difference constraints that are satisfied by all points in the zone.

2. Perform normalisation with respect to the maximum constants of


![](content_assets/paper.pdf-0068-10.png)


   - .

3. Apply the negation of all the collected constraints to the normalised zone to make sure that none of the collected constraints are satisfied after normalisation.

In Algorithm 2 this core normalisation is given as pseudo code. The set referred to in the algorithm is the set of difference constraints in and the operation norm refers to normalisation with respect to the maximum constants of .

--- end of page.page_number=68 ---

57

Timed Automata with Constraints on Clock Differences

**Algorithm 2** Core normalisation algorithm **for all** such that or **do if then end if end for** norm **for all do end for return**

However, there are cases where this algorithm is incorrect with respect to the equivalence classes. For some cases when a difference constraint split the zone to be normalised, the perfect normalisation may not be represented using a single zone. One instance of such a zone is the “leaving S1” zone in our running example. If this zone was extended to contain the set of equivalence classes, from which it contains points, it would be the whole clock space except for the small triangle defined by . The main difference between the two proposed algorithms is how this is resolved.

## **4.3 Algorithm: Normalisation without Zone Splitting**

The first normalisation algorithm is based on the observation that due to the geometry of the equivalence classes, the problem will only occur when the zone is stretched downwards, _i.e._ when the lower bound of the zone is lowered down to the maximum constant. Thus, if the zones are not stretched downwards when normalising the problem can be avoided. This gives an algorithm that is similar to core normalisation presented in Algorithm 2, with the only exception that the step of replacing constraints of the form and for is removed from the norm -operation.

The problem with this solution is that the normalised zone graph is no longer finite, since delay may cause the lower bound of the zone to increase unboundedly. However, the normalised zones are well quasi-ordered with respect to zone inclusion and thus the termination of the reachability algorithm can be guaranteed [A CJT00].[ˇ]

--- end of page.page_number=69 ---

58

Timed Automata with Constraints on Clock Differences

Using this normalisation procedure for our example automaton will give the zones presented in Figure 5. We note from the figure that now the normalised zones does not contain time assignments from equivalence classes not in the corresponding unnormalised zone. Further we see that the zones are not expanded to fill all the equivalence classes where it has points.

## **4.4 Algorithm: Normalisation with Zone Splitting**

The second normalisation procedure is based on the observation that the problem only occurs when a difference constraint divides the unnormalised zone, _i.e._ some of the time assignments in the zone satisfy the difference constraint and some do not. Thus, if all such zones are split along dividing difference constraints, _e.g._ using Algorithm 3, before normalisation this problem can be avoided.

**Algorithm 3** Zone splitting algorithm


![](content_assets/paper.pdf-0070-06.png)



![](content_assets/paper.pdf-0070-07.png)



![](content_assets/paper.pdf-0070-08.png)



![](content_assets/paper.pdf-0070-09.png)



![](content_assets/paper.pdf-0070-10.png)



![](content_assets/paper.pdf-0070-11.png)


**for all do for all do if** and **then else end if end for end for return**


![](content_assets/paper.pdf-0070-13.png)



![](content_assets/paper.pdf-0070-14.png)


The full normalisation procedure is presented in Algorithm 4. The splitting, denoted by split in the description, is used as a preprocessing step and then the basic normalisation algorithm, norm , is applied to all the resulting zones. We use norm to denote this normalisation operation and we use this operation to define a normalised symbolic transition relation.

**Definition 4** _Let be a timed automaton with the symbolic semantics . The -normalised version of ( ) for is defined by: whenever then for all norm ._

--- end of page.page_number=70 ---

59

Timed Automata with Constraints on Clock Differences

**Algorithm 4** Splitting normalisation algorithm


![](content_assets/paper.pdf-0071-03.png)



![](content_assets/paper.pdf-0071-04.png)


**for all** split **do** norm **end for return**


![](content_assets/paper.pdf-0071-06.png)


To demonstrate the normalisation procedure we apply it to our running example. In Figure 6 we see the zones from the -normalised transition relation. The two first states are not affected by normalisation so they are the same as in the unnormalised semantics. The zone for the next state, the “Leaving ” state, have both time assignments satisfying the constraint and time assignment satisfying . Thus we have to split the state before normalisation. The two resulting states are and . When normalising these states we get and , respectively. After the next step only one of the states remain, the other did not satisfy the guard on the transition. The state is now . After idling in the state is . This state does not satisfy the constraint , and thus location is not reachable.

Before proving the correctness of the -normalised transition relation, we need to establish some properties of the norm operator.

**Lemma 1** _Assume a timed automaton , with associated norm operator. For any zone the following holds._

- _(1) For all constraints mentioned in , norm norm_


![](content_assets/paper.pdf-0071-11.png)



![](content_assets/paper.pdf-0071-12.png)



![](content_assets/paper.pdf-0071-13.png)



![](content_assets/paper.pdf-0071-14.png)



![](content_assets/paper.pdf-0071-15.png)



![](content_assets/paper.pdf-0071-16.png)



![](content_assets/paper.pdf-0071-17.png)



![](content_assets/paper.pdf-0071-18.png)



![](content_assets/paper.pdf-0071-19.png)



![](content_assets/paper.pdf-0071-20.png)



![](content_assets/paper.pdf-0071-21.png)


- _(2) norm norm_

- _(3) norm norm norm_


![](content_assets/paper.pdf-0071-24.png)



![](content_assets/paper.pdf-0071-25.png)


_Proof:_ (sketch) These properties are proved by reasoning about how the , and operations modify the zones with respect to the two types of constraints that effect normalisation, _i.e._ non-difference constraints with bounds above the maximum constants and difference constraints.

- (1) Adding a guard of the form will cut the zone along one of the normalisation split lines. If this is done before normalisation the result will be that normalisation produce a subset of the zones that it

--- end of page.page_number=71 ---

Timed Automata with Constraints on Clock Differences

60

would originally have produced. If the guard is added after normalisation a number of entire zones from the normalisation will be removed giving

Adding a guard of the form will cut away a part of the zone that is not affected by the normalisation since, by definition,

- (2) Difference constraints are not effected at all by the operation. Further do not introduce any new non-difference constraints.


![](content_assets/paper.pdf-0072-05.png)


- (3) operations are projections of a on a hyperplane defined by . This projection has the property that points that were added by normalisation are mapped to other that would be added by renormalisation.

Finally we prove that the -normalised transition relation is correct.

**Theorem 1** _Let be a timed automaton and for each clock let be the largest number is compared to in ._


![](content_assets/paper.pdf-0072-09.png)



![](content_assets/paper.pdf-0072-10.png)


- _(Soundness) whenever then for all such that (Completeness) whenever then for some such that_


![](content_assets/paper.pdf-0072-12.png)



![](content_assets/paper.pdf-0072-13.png)



![](content_assets/paper.pdf-0072-14.png)



![](content_assets/paper.pdf-0072-15.png)



![](content_assets/paper.pdf-0072-16.png)



![](content_assets/paper.pdf-0072-17.png)



![](content_assets/paper.pdf-0072-18.png)



![](content_assets/paper.pdf-0072-19.png)



![](content_assets/paper.pdf-0072-20.png)



![](content_assets/paper.pdf-0072-21.png)



![](content_assets/paper.pdf-0072-22.png)



![](content_assets/paper.pdf-0072-23.png)



![](content_assets/paper.pdf-0072-24.png)



![](content_assets/paper.pdf-0072-25.png)



![](content_assets/paper.pdf-0072-26.png)



![](content_assets/paper.pdf-0072-27.png)



![](content_assets/paper.pdf-0072-28.png)



![](content_assets/paper.pdf-0072-29.png)


_Proof:_ Both soundness and completeness are proven by induction on the length of the transition sequences.

_(Soundness)_ As induction hypothesis, assume such that and norm . Further assume . We now need to prove that such that norm , and norm . We have two cases: delay transitions and action transitions.


![](content_assets/paper.pdf-0072-32.png)


(Delay) By the assumption by delay, and the definition of we get norm . Combining this with Lemma 1 (1+2) gives norm norm , and since is already normalised we get , _i.e._ . Now assume that for all such that norm and by delay, norm . By the definition of we have , which gives norm norm . Expansion using Lemma 1 (1+2) yields norm

--- end of page.page_number=72 ---

Timed Automata with Constraints on Clock Differences

61

norm . By our assumption, norm and norm , for all , but this lead to a contradiction.


![](content_assets/paper.pdf-0073-03.png)



![](content_assets/paper.pdf-0073-04.png)



![](content_assets/paper.pdf-0073-05.png)



![](content_assets/paper.pdf-0073-06.png)



![](content_assets/paper.pdf-0073-07.png)


- (Action) By assumption we know that by . From the definitions of norm and we can derive that

- for all such that norm , by Now we need to prove that such that

- norm . By the definition of , norm norm . Expansion by Lemma 1(1) gives norm norm . According to Lemma 1(1+3) and

- norm we have norm norm .

- And since we know, by the definition of , that norm we conclude that norm .

_(Completeness)_ As induction hypothesis, assume such that and . Further assume . We need to prove that such that , and . There are two cases, or .


![](content_assets/paper.pdf-0073-10.png)



![](content_assets/paper.pdf-0073-11.png)



![](content_assets/paper.pdf-0073-12.png)



![](content_assets/paper.pdf-0073-13.png)



![](content_assets/paper.pdf-0073-14.png)



![](content_assets/paper.pdf-0073-15.png)


- ( ) By the assumption we know , _i.e._ . From the

- definition of we have by delay, if norm . Expansion by the definition of yields norm . By the definition of norm we know that for all zones , norm . Thus there is a zone norm such that


![](content_assets/paper.pdf-0073-17.png)



![](content_assets/paper.pdf-0073-18.png)


- ( ) By the assumption we know , , . From the definition of we have by if norm

- . Expanding this by the definition of the -operation yields

- norm . By the def-

- inition of norm we know that for all zones , norm . Thus there is a zone norm such that .

--- end of page.page_number=73 ---

Timed Automata with Constraints on Clock Differences

62


![](content_assets/paper.pdf-0074-02.png)


Figure 5: Zones for the example automaton, with non splitting normalisation.


![](content_assets/paper.pdf-0074-04.png)


Figure 6: Zones for the example automaton, with splitting normalisation.

--- end of page.page_number=74 ---

Timed Automata with Constraints on Clock Differences

63

## **5 Conclusion**

In modelling and verifying timed systems, using timed automata, constraints over clock differences are useful and needed in many applications e.g. solving scheduling problems. In this paper, we have reported a problem in the existing (published) symbolic reachability algorithms for timed automata. The problem is that the existing normalisation algorithms (implemented by several verification tools for timed automata e.g. UPPAAL) for clock constraints based on region equivalence are incorrect in the sense that they may provide wrong answers in verifying timed automata containing constraints on clock differences. The reason is that the normalisation operations may enlarge a zone so that the guard (a difference constraint) labelled on a transition is made true and thus incorrectly enables the transition. Thus the normalisation operation should be based on a finer equivalence relation than region equivalence. We propose to use the region equivalence which is further refined by difference constraints. Based on this, we have developed two normalisation algorithms that allow not only clock comparison with naturals but also comparison between clocks i.e. constraints on clock differences. The algorithms transform DBM’s according to not only the maximal constants of clocks but also difference constraints appearing in an automaton. To our knowledge, they are the first published normalisation algorithms for timed automata containing difference constraints. The algorithms have been implemented in UPPAAL showing that almost no extra overhead is added to deal with difference constraints.

## **References**

- [ABB 01] Tobias Amnell, Gerd Behrmann, Johan Bengtsson, Pedro R. D’Argenio, Alexandre David, Ansgar Fehnker, Thomas Hune, Bertrand Jeannet, Kim G. Larsen, M. Oliver Möller, Paul Pettersson, Carsten Weise, and Wang Yi. UPPAAL - Now, Next, and Future. In _Modelling and Verification of Parallel Processes_ , number 2067 in Lecture Notes in Computer Science, pages 100–125. Springer-Verlag, 2001.

- [A CJT00][ˇ] Parosh Aziz Abdulla, K¯arlis Cer¯ans, Bengt Johnsson, and Yih-Kuen Tsay.[ˇ] Algorithmic analysis of programs with well quasi-ordered domains. _Journal of Information and Computation_ , 160:109–127, 2000.

- [AD94] Rajeev Alur and David L. Dill. A theory of timed automata. _Journal of Theoretical Computer Science_ , 126(2):183–235, 1994.

--- end of page.page_number=75 ---

Timed Automata with Constraints on Clock Differences

64

- [BDGP98] Beatrice Bérard, Volker Diekert, Paul Gastin, and Antoine Petit. Characterization of the expressive power of silent transitions in timed automata. _Fundamenta Informaticae_ , 36:145–182, 1998.

- [Bel57] Richard Bellman. _Dynamic Programming_ . Princeton University Press, 1957.

- [BLL 96] Johan Bengtsson, Kim G. Larsen, Fredrik Larsson, Paul Pettersson, and Wang Yi. UPPAAL in 1995. In _Proc. of the 2_ nd _Workshop on Tools and Algorithms for the Construction and Analysis of Systems_ , number 1055 in Lecture Notes in Computer Science, pages 431–434. Springer–Verlag, March 1996.

- [Dil89] David L. Dill. Timing assumptions and verification of finite-state concurrent systems. In _Proceedings, Automatic Verification Methods for Finite State Systems_ , volume 407 of _Lecture Notes in Computer Science_ , pages 197–212. Springer-Verlag, 1989.

- [DOTY95] Conrado Daws, Alfredo Olivero, Stavros Tripakis, and Sergio Yovine. The tool kronos. In _Proceedings, Hybrid Systems III: Verification and Control_ , volume 1066 of _Lecture Notes in Computer Science_ . Springer-Verlag, 1995.

- [Hig52] Graham Higman. Ordering by divisibility in abstract algebras. _Proceedings of the London Mathematical Society, Ser. 3_ , 2:326–336, 1952.

- [HNSY92] Thomas A. Henzinger, Xavier Nicollin, Joseph Sifakis, and Sergio Yovine. Symbolic model checking for real-time systems. In _Proceedings, Seventh Annual IEEE Symposium on Logic in Computer Science_ , pages 394–406, 1992.

- [HNSY94] Thomas A. Henzinger, Xavier Nicollin, Joseph Sifakis, and Sergio Yovine. Symbolic model checking for real-time systems. Technical Report TR941404, Cornell Computer Science Technical Report Collection, 1994.

- [LPY95] Kim G. Larsen, Paul Pettersson, and Wang Yi. Compositional and Symbolic Model-Checking of Real-Time Systems. In _Proc. of the 16_ th _IEEE Real-Time Systems Symposium_ , pages 76–87. IEEE Computer Society Press, December 1995.

- [LPY97] Kim G. Larsen, Paul Petterson, and Wang Yi. Uppaal in a nutshell. _Journal on Software Tools for Technology Transfer_ , 1997.

- [Pet99] Paul Pettersson. _Modelling and Verification of Real-Time Systems Using Timed Automata: Theory and Practice_ . PhD thesis, Uppsala University, 1999.

- [Rok93] Tomas Gerhard Rokicki. _Representing and Modeling Digital Circuits_ . PhD thesis, Stanford University, 1993.

--- end of page.page_number=76 ---

65

Timed Automata with Constraints on Clock Differences

- [YL93] Mihalis Yannakakis and David Lee. An efficient algorithm for minimizing real-time transition systems. In _Proceedings, Fifth International Conference on Computer Aided Verification_ , volume 697 of _Lecture Notes in Computer Science_ , pages 210–224. Springer-Verlag, 1993.

- [Yov97] Sergio Yovine. Kronos: A verification tool for real-time systems. _Journal on Software Tools for Technology Transfer_ , 1, October 1997.

- [Yov98] Sergio Yovine. Model checking timed automata. In _European Educational Forum: School on Embedded Systems_ , volume 1494 of _Lecture Notes in Computer Science_ , pages 114–152. Springer-Verlag, 1998.

- [YPD94] Wang Yi, Paul Petterson, and Mats Daniels. Automatic verification of realtime communicating systems by constraint-solving. In _Proceedings, Seventh International Conference on Formal Description Techniques_ , pages 223–238, 1994.

--- end of page.page_number=77 ---

--- end of page.page_number=78 ---

## **Paper C:**

**Reducing Memory Usage in Symbolic State-Space Exploration for Timed Systems**

Johan Bengtsson and Wang Yi.

--- end of page.page_number=79 ---

--- end of page.page_number=80 ---

69

Reducing Memory Usage

## **Reducing Memory Usage in Symbolic State-Space Exploration for Timed Systems**

## Johan Bengtsson and Wang Yi

Department of Computer Systems, Uppsala University, Sweden. Email: {johanb,yi}@docs.uu.se

**Abstract.** One of the major problems in scaling up model checking techniques to the size of industrial systems is memory consumption. This paper studies the problem in the context of verifiers for timed automata. We present a number of techniques that reduce the amount of memory used in symbolic reachability analysis. We address the memory consumption problem on two fronts. First, we reduce the size of internal representations for each symbolic state (clock constraints) by means of compression methods. Second, we reduce the explored state space (list of symbolic states) by early-inclusion checking between states and by probabilistic methods. These techniques have been implemented in the UPPAAL tool. Their strengths and weaknesses are evaluated and compared in experiments using real-life examples. Note that though these techniques are developed for timed systems, they are of general interests for verification tool development, in particular to handle large symbolic states based on constraint representation and manipulation.

## **1 Introduction**

During the last ten years timed automata [AD90, AD94] have evolved as a common model to describe timed systems. This process has gone hand in hand with the development of verification tools for timed automata, such as KRONOS [DOTY95, Yov97] and UPPAAL [LPY97, ABB 01]. One of the major problems in applying these tools to industrial-size systems is the large memory consumption ( _e.g._ [BGK 96]) when exploring the state space of a network of timed automata. The reason is that the exploration not only suffers from the large number of states to be explored, but also from the large size of each state. In this paper we address both these problems.

We will present techniques to reduce memory usage for internal representations of symbolic states by means of compaction. We use two different methods for packing states. First, we code the entire state as one large number us-

--- end of page.page_number=81 ---

Reducing Memory Usage

70

ing a multiply-and-add algorithm. This method yields a representation that is canonical and minimal in terms of memory usage but the performance for inclusion checking between states is poor. The second method is mainly intended to be used for the timing part of the state and it is based on concatenation of bit strings. Using a special concatenation of the bit string representation of the constraints in a zone, ideas from [PS80] can be used to implement fast inclusion checking between packed zones.

Furthermore, we attack the problem with large state spaces in two different ways. First, to get rid of states that do not need to be explored, as early as possible, we introduce inclusion checking already in the data structure holding the states waiting to be explored. We also describe how this can be implemented without slowing down the verification process. Second, we investigate how supertrace [Hol91] and hash compaction [WL93, SD95] methods can be applied to timed systems. We also present a variant of the hash compaction method, that allows termination of branches in the search tree based on probable inclusion checking between states.

The rest of the paper is organised as follows: In section 2 we introduce timed automata and describe briefly how to check reachability properties for timed automata. In section 3 we present methods to represent the key objects used in checking timed automata, namely the symbolic states. We also give a comparison between them. Section 4 addresses issues on the whole state space of an automaton. We describe how the wait and past lists are handled efficiently. We also describe an approximation method of the past list that can be used when the complete state space of an automaton is too big to be stored in memory. Finally, section 5 wraps up the paper by summarising the most important results and suggests some directions for future work.

## **2 Preliminaries**

In this section we briefly review background materials including timed automata and reachability analysis based on clock constraints. A more extensive description can be found in _e.g._ [AD94, Pet99].

Let be a finite set of labels, ranged over by _etc._ A timed automaton is a finite state automaton over alphabet extended with a set of real valued clocks, to model time dependent behaviour. Let denote a set of clocks, ranged over by . Let denote the set of conjunctions of atomic constraints of the

--- end of page.page_number=82 ---

Reducing Memory Usage

71

form or for and . We use and later to range over this set.

**Definition 5 (Timed Automaton)** _A timed automaton is a tuple where is a set of control nodes, is the initial node, is the set of edges and assign invariants to locations. As a convention we will use to denote ._

The clock values are formally represented as functions, called clock assignments, mapping to the non-negative reals . We let denote such functions, and use to denote that the clock assignment satisfy the formula . For we let denote the clock assignment that map all clocks in to the value , and for we let denote the clock assignment that map all clocks in to 0 and agree with for all clocks in .

The semantics of a timed automaton is a timed transition-system where the states are pairs , with two types of transitions, corresponding to delay transitions and discrete action transitions respectively:


![](content_assets/paper.pdf-0083-06.png)



![](content_assets/paper.pdf-0083-07.png)



![](content_assets/paper.pdf-0083-08.png)



![](content_assets/paper.pdf-0083-09.png)



![](content_assets/paper.pdf-0083-10.png)



![](content_assets/paper.pdf-0083-11.png)



![](content_assets/paper.pdf-0083-12.png)



![](content_assets/paper.pdf-0083-13.png)



![](content_assets/paper.pdf-0083-14.png)


if and


![](content_assets/paper.pdf-0083-16.png)



![](content_assets/paper.pdf-0083-17.png)



![](content_assets/paper.pdf-0083-18.png)



![](content_assets/paper.pdf-0083-19.png)



![](content_assets/paper.pdf-0083-20.png)



![](content_assets/paper.pdf-0083-21.png)



![](content_assets/paper.pdf-0083-22.png)


if and


![](content_assets/paper.pdf-0083-24.png)



![](content_assets/paper.pdf-0083-25.png)



![](content_assets/paper.pdf-0083-26.png)


It is easy to see that the state space is infinite and thus not a good base for algorithmic verification. However, efficient algorithms may be obtained using a _symbolic semantics_ based on _symbolic states_ of the form [HNSY92, YPD94] where is the location vector of an automaton and is a clock constraint (zone) specifying the clock values. They are symbolic in the sense that the clock zone represents a set of concrete states of the automaton with the same control location vector. The symbolic counterpart of the transitions are given by:


![](content_assets/paper.pdf-0083-28.png)



![](content_assets/paper.pdf-0083-29.png)



![](content_assets/paper.pdf-0083-30.png)



![](content_assets/paper.pdf-0083-31.png)



![](content_assets/paper.pdf-0083-32.png)



![](content_assets/paper.pdf-0083-33.png)



![](content_assets/paper.pdf-0083-34.png)



![](content_assets/paper.pdf-0083-35.png)



![](content_assets/paper.pdf-0083-36.png)



![](content_assets/paper.pdf-0083-37.png)



![](content_assets/paper.pdf-0083-38.png)



![](content_assets/paper.pdf-0083-39.png)



![](content_assets/paper.pdf-0083-40.png)



![](content_assets/paper.pdf-0083-41.png)



![](content_assets/paper.pdf-0083-42.png)



![](content_assets/paper.pdf-0083-43.png)



![](content_assets/paper.pdf-0083-44.png)



![](content_assets/paper.pdf-0083-45.png)



![](content_assets/paper.pdf-0083-46.png)



![](content_assets/paper.pdf-0083-47.png)



![](content_assets/paper.pdf-0083-48.png)


where and . It can be shown that the set of constraint systems is closed under these operations. Moreover the symbolic semantics correspond closely to the standard semantics in the sense that if then, for all there is such that .

Given a timed automaton with an initial symbolic state and a final symbolic state , is said to be _reachable_ if

--- end of page.page_number=83 ---

Reducing Memory Usage

72

and for some . The reachability problem can be solved using a standard reachability algorithm as shown in Algorithm 1 for graphs with a proper normalisation algorithm for clock constraints [Pet99, Rok93] (to guarantee termination).

The algorithm uses two important data structures: WAIT and PASSED. WAIT is a list of states waiting to be explored and PASSED is the set of states already explored. Due to the size of the state space, these structures may consume a considerable amount of main memory. The main objective of this paper is to present techniques to reduce the memory usage of these two structures.

## **Algorithm 1** Symbolic reachability analysis

PASSED WAIT **while** WAIT **do** take from WAIT **if then return** “YES” **if** for all PASSED **then** add to PASSED **for all** such that **do** add to WAIT **end for end if end while return** “NO”

The core of the above reachability algorithm is manipulation and representation of symbolic states. So symbolic states are the core objects of state space search, and one of the key issues in implementing an efficient model checker is how to represent them. The desired properties of the representation also differ in parts of the verifier, and there are potential gains in using different representations in different places.

The encoding of the location vector and the integer assignment is straight forward. For the location vector we number the locations in each process, to get a vector of location numbers. Representing the clock zone is a bit trickier but starting from the constraint system representation of a zone it is possible to obtain an efficient intermediate representation. We start with the following observation: Let be a dummy clock with the constant value 0. Then for each constraint system there is a constraint system with the same solution set as , and where all constraints are of the form or , for .

--- end of page.page_number=84 ---

Reducing Memory Usage

73

We also note that to represent any clock zone we need at most atomic constraints. One of the most compact ways to represent this is to use a matrix where each element represent a bound on the difference between two clocks. Each element in the matrix is a pair where is an integer and tells whether the bound is strict or not. Such a matrix is called a _Difference Bounds Matrix_ , or _DBM_ for short. More detailed information about DBMs can be found in [Dil89].

## **3 Representing Symbolic States**

Recall that symbolic states are pairs in the form where is the location vector of an automaton represented as a vector of integers and is a clock constraint (zone), represented as a matrix of integers (DBM). Logically such a state is a vector of integers representing the control locations and clock bounds. In the following, we study how to represent the vectors physically in the main memory for efficient storage and manipulation.

## **3.1 Normal Representation**

The simplest way to physically represent a symbolic state is to use a machine word for each control location, integer value or clock bound. The implementation is straight forward, but a practical tip is that if the standard library functions for memory management are used all the memory needed for one state should, if possible, be allocated in the same chunk, to minimise the allocation overhead.

The strength of this representation is its simplicity and the speed of accessing an individual control location, integer value, or clock bound. In this representation the maximum time needed to reach any individual entity is the time needed to fetch a word from the memory. This makes the representation ideal to use when we have to do operations on individual entities, _e.g._ when calculating the successors of a state. The weakness is the amount of wasted space. Here a whole machine word, typically 32-bit wide, is used to store entities where all possible values may fit in many fewer bits.

However this is a good base representation for states. It is ideal for states that will be modified in the near future, such as intermediate states or states in WAIT. It also works reasonably well for states in PASSED, specially for small and medium sized examples.

--- end of page.page_number=85 ---

Reducing Memory Usage

74

This representation is used for both WAIT and PASSED in the current version of UPPAAL.

## **3.2 Packed States**

The second representation is on the opposite side of the spectrum compared to the previous one and it can be used for the discrete part of the states, for the clock zone and for both together. The encoding builds on a simple multiply and add scheme, similar to the position system for numbers, and it is very compact. In the description we will focus on encoding an entire symbolic state, but the parts can also be encoded separately.

First, consider the state as a vector , where each element represents a control location, the value of a variable, or a clock bound. For each element we can compute the number of possible values, . For the location vector is the number of control locations in the corresponding process, for the integer assignment is the size of the domain of the corresponding variable and for the clock zone then can be computed using the maximum constant .

Now consider the vector as a number written down in a position system with a variable base, _i.e._ each element is a digit and the product is its position value. Represent the state as the value of this number, _i.e._ encode the state as follows:


![](content_assets/paper.pdf-0086-07.png)



![](content_assets/paper.pdf-0086-08.png)



![](content_assets/paper.pdf-0086-09.png)



![](content_assets/paper.pdf-0086-10.png)



![](content_assets/paper.pdf-0086-11.png)



![](content_assets/paper.pdf-0086-12.png)



![](content_assets/paper.pdf-0086-13.png)



![](content_assets/paper.pdf-0086-14.png)



![](content_assets/paper.pdf-0086-15.png)



![](content_assets/paper.pdf-0086-16.png)



![](content_assets/paper.pdf-0086-17.png)



![](content_assets/paper.pdf-0086-18.png)



![](content_assets/paper.pdf-0086-19.png)



![](content_assets/paper.pdf-0086-20.png)


Note that the representation of states using multiply-and-add encoding is canonical and minimal in terms of space usage. Note also that in this context is a sequence of numbers. The encoding is a number. The resulted numbers are often too large to fit in a machine word and they have to be in fixed precision; thus we need some kind of arbitrary precision numbers for the encoding. In our prototype implementation we used the GMP package [Gra00].

The strength of this representation is the effective use of space and the weakness is that to access an individual integer value or clock bound a number of division and modulo operations must be performed. This results in small states that are expensive to handle.

--- end of page.page_number=86 ---

75

Reducing Memory Usage

|Example|Time|Time|Space|Space|
|---|---|---|---|---|
||real (Sec)|relative|real (MB)|relative|
|Field Bus (Faulty 1)|||||
|Field Bus (Faulty 2)|||||
|Field Bus (Faulty 3)|||||
|Field Bus (Fixed)|||||
|B&O|||||
|DACAPO (big)|||||
|DACAPO (small)|||||
|Fischer 5|||||
|Fischer 6|||||



Table 1: Performance for packed states with expensive inclusion checking

In order to test the performance of this representation, it is implemented in the PASSED structure in UPPAAL. The implementation is straight forward, however expensive division and modulo operations have to be used, in order to compare the DBMs bound by bound.

The result of the experiment is presented in Table 1 (as absolute figures and in relation to the current PASSED implementation in UPPAAL). We note that with this representation the space performance is very good, with reductions of up to 70% compared to the current PASSED implementation. However the time performance is poor, for one instance of Fischers protocol we notice a slowdown of almost 13 times and for one instance of the Field Bus protocol the slowdown is 8 times. The conclusion is that this representation should only be used in cases where main memory is a severe restriction.

## **3.3 Packed Zones with Cheap Inclusion Check**

The main drawback of representing states using the number encoding given in section 3.2 is expensive inclusion checking. In this section we present a compact way of representing zones overcoming this drawback. The heart of this representation builds on an observation due to [PS80] that one subtraction can be used to perform multiple comparisons in parallel.

Let denote the minimum number of bits needed to store all possible values for one clock bound. The DBM is then encoded as a long bit string, where each bound is assigned a bit wide slot. The value of the clock bound is put in

--- end of page.page_number=87 ---

76

Reducing Memory Usage

the least significant bits in the slot and the extra, most significant bit, is used as a _test bit_ .

Since a zone is included in another zone if and only if each bound in the DBM representing is as tight as the same bound in the DBM representation of , inclusion checking is to check if all elements in one vector is less than or equal to the same bound in another vector. Using the new bit-string encoding of zones this can be checked using only simple operations like bitwise-and ( ), bitwise-or ( ), subtraction and test for equality.

Given two packed zones and , to check if first set all the test bits in to zero and all the test bits in to one. In an implementation the test bits are usually zero in the stored states and setting them to one is done using a prefabricated mask . The test is then performed by calculating . The result is read out of the test bits. If a test bit is one the corresponding bound in is at least as tight as in and if a test bit is zero the corresponding bound is tighter in than in . Thus, if all test bits are one we can conclude that and if all the test bits are zero . It is worth noting that “all test bits are one” is both necessary and sufficient to conclude while “all test bits are zero” is only sufficient to conclude .

In an implementation of this scheme the main issue is how to handle the bit strings. The easiest way is to let a bignum package handle everything. However, this may give a considerable overhead, specially in connection with memory allocation, since the bignum packages are often tailored towards other types of applications. In UPPAAL we share the memory layout of the bignum packages, but to reduce the overhead we have implemented our own operations on top of it.

In the physical representation, _i.e._ how the bit-string is stored in memory, the bit-string is chopped up into machine-word sized chunks, or _limbs_ . The limbs are then packed in big-endian order, _i.e._ the least significant limb first, in an array. If the bit string doesn’t fill an even number of machine words the last limb is padded with zero bits.

Noting that the effect of all operations needed for the inclusion check, except subtraction, is local within the limb and that subtraction only passes one borrow bit to the next more significant limb, we can implement the inclusion check in one pass through the array of limbs instead of one pass for each operation. The one pass inclusion check is shown in Algorithm 2. In the description we use to denote the limb with index in and to denote a binary subtraction of machine word size.

--- end of page.page_number=88 ---

Reducing Memory Usage

77

**Algorithm 2** Inclusion check for packed zones


![](content_assets/paper.pdf-0089-03.png)



![](content_assets/paper.pdf-0089-04.png)



![](content_assets/paper.pdf-0089-05.png)


**for to** limbs **do** cmp **if** cmp **then return** “false” **if then else end if end for return** “true”


![](content_assets/paper.pdf-0089-07.png)


|Example|Time|Space|
|---|---|---|
||real (Sec)<br>relative<br>real (MB)<br>relative||
|Field Bus (Faulty 1)|||
|Field Bus (Faulty 2)|||
|Field Bus (Faulty 3)|||
|Field Bus (Fixed)|||
|B&O|||
|DACAPO (big)|||
|DACAPO (small)|||
|Fischer 5|||
|Fischer 6|||



Table 2: Performance for packed states with cheap zone coding

To evaluate the performance of this technique, it was implemented in the PASSED structure in UPPAAL. In the experiment the discrete part of each state is stored in PASSED using the compact representation from the previous section and the zone is stored using this technique. The results are presented in Table 2, both as absolute figures and compared to the standard state representation. We note that using this method the space usage is typically reduced by about 40%, without increased verification time. The verification time is actually reduced a little using this scheme, even though the number of operations is increased. The reason for this is most certainly that the number of memory operations are reduced by the smaller memory footprint of the states[1] .

> 1Memory operations are expensive compared to arithmetic operations, specially since there is no temporal locality in verifiers.

--- end of page.page_number=89 ---

Reducing Memory Usage

78

## **4 Representing the Symbolic State-Space**

The two key data structures in a model checker are, as mentioned before, WAIT, that keeps track of states not yet explored, and PASSED, that keeps track of states already visited. Both these data structures tend to be large, and how to represent them is an important issue for performance. In this section we describe how to implement WAIT and how to improve its performance by adding inclusion checking. We also describe a standard implementation of PASSED as well as an implementation where space is saved at the price of possibly inconclusive answers.

## **4.1 Representing WAIT**

In its most simple form WAIT is implemented as a linked list. This is easy to implement and it is easy to control the search order by adding unexplored states at the end, for breadth first search, or adding states at the beginning, for depth

An optimisation in terms of both time and space is to check whether a state already occur in WAIT before adding it. For a verifier based on explicit states this will only give minor improvements, mainly by keeping down the length of WAIT, but for a verifier based on symbolic states this may actually prevent revisiting parts of the state space.

We know, _e.g._ from [Pet99], that if then all states reachable from are also reachable from and thus we only have to explore . So before adding a new state to WAIT we check all states already in WAIT. If we find any state including we stop searching and throw away since all states reachable from it are also reachable from a state already scheduled for exploration. If no such state is found we add to WAIT. During the search through WAIT we also delete all states included in in order to prevent revisiting parts of the state space.

There are some implementation issues that need consideration. The main issue is how to find all states in WAIT with same discrete part. The simplest way to do this is to do a linear search through WAIT every time a state is added. However, using this solution it will be expensive to add states, even for examples where WAIT is short. One solution to this is to implement WAIT using a structure where searching is cheap, _e.g._ a hash table. The problem with this solution is that picking up states from WAIT will be expensive, at least for search strategies

--- end of page.page_number=90 ---

Reducing Memory Usage

79


![](content_assets/paper.pdf-0091-02.png)


Figure 1: Structure of WAIT

|Example||Time (Sec)|||Space (MB)||
|---|---|---|---|---|---|---|
||no opt|inclusion|gain(%)|no opt|inclusion|gain(%)|
|Field Bus (Faulty 1)|||||||
|Field Bus (Faulty 2)|||||||
|Field Bus (Faulty 3)|||||||
|Field Bus (Fixed)|||||||
|B&O|||||||
|DACAPO (big)|||||||
|DACAPO (small)|||||||
|Fischer 5|||||||
|Fischer 6|||||||



Table 3: Performance impact of inclusion check on WAIT

like breadth first and depth first, where the exploration order depends on the order in which the states were added WAIT.

In the implemented solution, each state in WAIT is indexed using both a list and a hash table. The list part is used to keep the depth or breadth first ordering of states and to make it cheap to pick up states to explore. The hash table part is used to index the states in WAIT based on their location vector, in order to speed up inclusion checking. A picture of this structure is shown in Figure 1.

To test the performance of this solution we compared the space and time needed to explore the state space of nine examples, for one version of UPPAAL without inclusion checking on WAIT and one version with the combined scheme. The result is shown in Table 3. It is worth noting that the version with inclusion checking is both significantly faster and less memory consuming than the version without inclusion checking, for all examples except Fischers protocol which is, as mentioned in the appendix, not typical.

--- end of page.page_number=91 ---

Reducing Memory Usage

80

## **4.2 Representing PASSED**

The key feature needed by a representation of PASSED is that searching should be cheap. For a symbolic verifier it is also crucial, at least performance wise, that finding states which includes a given state is possible and cheap. In UPPAAL the standard PASSED is implemented as a hash table, where the key is computed from the discrete part of the state and collisions are handled by chaining. The reason for basing the hash key only on the discrete part is to simplify checking for inclusion between states by making all related states end up in the same hash bucket. It is easy to see that hashing only on the discrete part is as good as we can do if we want this property. The reason for using chaining instead of open addressing to resolve conflicts is, apart from keeping related states together, mainly simplicity and eliminating the need for expensive rehashing. Judging by performance the choice could go either way, at least if rehashing is not taken into account. More about this can be read in [Lar00].

For some models the memory needed for exact verification may exceed the amount of memory installed in the system where the verification takes place. This often occurs within the modelling phase before most bugs are removed from the model. During this phase the verification engine is often used as a tool to find the cause of unwanted behaviour and not primarily to prove the absence of such behaviour. Under these premises it is desirable to use a method that can handle larger systems but sometimes miss unwanted behaviour. Here we will describe two such methods. The first method is an application of the supertrace algorithm from [Hol91] on networks of timed automata. The second method is based on the hash compaction method from [WL93, SD95].

## **4.3 Supertrace PASSED for Timed Automata**

The main idea behind supertrace PASSED is from the following observation: The purpose of PASSED is only to keep track of whether a state have been visited or not, _i.e._ for each state we only need one bit of information. Thus, PASSED for a system of states can be implemented as an -bit wide bit vector. However, if is sufficiently large, even such a compact representation will be too large to fit the memory of the system running the verifier. A way to tackle this problem is to loosen the demand that the verification should be exact and allow false hits to be indicated, _i.e._ a previously unvisited state may, with some probability, be reported as already visited. Such a false hit will be called an _omission_ , as it causes a part of the state space to be omitted from the state space

--- end of page.page_number=92 ---

Reducing Memory Usage

81

search. This affects the reachability search such that if a state is reported to be not reachable we can not conclude that it can not be reached since it might have been excluded by an omission.

The natural way to implement such a PASSED structure is to allocate a bitvector of size , where , and hash each state to a value in . In the UPPAAL implementation of the supertrace algorithm the hash function is similar to the first packing technique described in Section 3:


![](content_assets/paper.pdf-0093-04.png)



![](content_assets/paper.pdf-0093-05.png)



![](content_assets/paper.pdf-0093-06.png)



![](content_assets/paper.pdf-0093-07.png)



![](content_assets/paper.pdf-0093-08.png)



![](content_assets/paper.pdf-0093-09.png)



![](content_assets/paper.pdf-0093-10.png)



![](content_assets/paper.pdf-0093-11.png)



![](content_assets/paper.pdf-0093-12.png)



![](content_assets/paper.pdf-0093-13.png)



![](content_assets/paper.pdf-0093-14.png)



![](content_assets/paper.pdf-0093-15.png)



![](content_assets/paper.pdf-0093-16.png)



![](content_assets/paper.pdf-0093-17.png)



![](content_assets/paper.pdf-0093-18.png)



![](content_assets/paper.pdf-0093-19.png)



![](content_assets/paper.pdf-0093-20.png)



![](content_assets/paper.pdf-0093-21.png)



![](content_assets/paper.pdf-0093-22.png)



![](content_assets/paper.pdf-0093-23.png)



![](content_assets/paper.pdf-0093-24.png)



![](content_assets/paper.pdf-0093-25.png)



![](content_assets/paper.pdf-0093-26.png)



![](content_assets/paper.pdf-0093-27.png)


Note that a variation of this hash function (applied only to the location vector and the integer assignment) is used in both the normal PASSED implementation and the cross-reference table of the WAIT list. It is also possible to enhance the supertrace algorithm by implementing a way to change the hash function between runs, in order to lower the probability that a part of the state space is omitted. A simple way to do this is to implement a generator of _universal_ hash functions [CW79] and provide the user with a way to choose among the functions in the class.

The main drawback of the supertrace algorithm, when applied to timed automata, is that inclusion between time zones can not be detected. The effect of this is that the number of explored states increases. This leads to longer verification times and more states to enter in PASSED, with an increased omission probability as result.

To investigate the performance of this algorithm we have implemented it in UPPAAL. In the experiment we test the supertrace PASSED structure for three different sizes: 16MB, 32MB and 64MB and compare it to the standard PASSED implementation of UPPAAL, to estimate the impact of collisions. The results of the experiment are presented in Table 4. For each of the examples the table shows the collision frequency and an estimation on the fraction of the state space not covered due to collisions.

In the table there are several interesting observations. First, for the Philips example the coverage is totally independent of the size of the PASSED structure. We get exactly the same collision frequency and coverage for all three runs. This is an indication that the hash function is far from optimal on this example.

--- end of page.page_number=93 ---

Reducing Memory Usage

82

|Example|16MB|16MB|32MB|32MB|64MB|64MB|
|---|---|---|---|---|---|---|
||collision|omitted|collision|omitted|collision|omitted|
|Philips (Correct)|||||||
|B&O|||||||
|DACAPO (big)|||||||
|DACAPO (small)|||||||
|Fischer 5|||||||
|Fischer 6|||||||



Table 4: Frequency of collisions and the fraction of state space not covered (in ) for three instances of the supertrace PASSED structure

|Example||Supertrace||Classic|
|---|---|---|---|---|
||16MB|32MB|64MB||
|Philips (Correct)|||||
|Philips (Erroneous)|||||
|B&O|||||
|DACAPO (big)|||||
|DACAPO (small)|||||
|Fischer 5|||||
|Fischer 6|||||



Table 5: Time (in seconds) to explore the entire state space for three different supertrace PASSED lists for the standard PASSED list

We also note, when studying the big DACAPO example, that even though the collision frequency is decreased the fraction of the state space not covered in the search may increase. The reason for this may be that the collisions occur for different states in the different runs and that the number of children for these states differ. (If a state with many children is omitted the coverage will be less than if a state with few children is omitted.)

To see how the supertrace algorithm behave time-wise we made an experiment where the verification time was measured and compared to the standard PASSED implementation in UPPAAL. The setting of this experiment is a little different from the previous one. For this example we used inclusion checking on WAIT, to speed up verification. This is the most likely setting when using the tool in practice. The result of this experiment is presented in Table 5. As we see in the table the times for the supertrace is in the same order of magnitude as the standard PASSED implementation.

--- end of page.page_number=94 ---

Reducing Memory Usage

83

## **4.4 Hash Compaction for Timed Automata**

Hash compaction evolved from the supertrace ideas as a way to lower the probability of omissions in the verification process. It was first investigated in [WL93] and then further developed in [SD95].

The key observation for hash compaction is that the supertrace PASSED list can be seen as representation of a set of hash values, where a set bit (1) in the table represents that this hash value is in the set; while an unset bit (0) in the table represent that it is not. Under the assumption that the set is sparse, _i.e._ the number of elements in the set is small compared to the number of elements not in it, a table of the elements might be a more compact representation of the set. With this solution the number of possible hash values is no longer bounded by the number of bits in the main memory.

In the work presented in [WL93] a normal hash table is used to store the elements and the key into this table is computed from the elements themselves. In [SD95] the technique is developed further. As a way to decrease the probability of false collisions the key into the table is computed from the state itself, instead of from the hash signature, using a different hash function. Since the hash signature and its entry in the table are computed using different hash functions two states have to collide in both the hash functions for a false collision to occur.

There is an alternative way to view this second variation of hash compaction. Start with the supertrace PASSED list. To lower the probability of classifying an unvisited state as already visited we increase the number of bits in each entry of the hash table. (Given a fixed amount of memory this is done at the expense of the number of entries in the table.) To separate different states that end up at the same position in table we build a signature, _e.g._ a checksum, of the states and store this. To compute the checksum we choose a function with a low probability that two different states have the same signature, _i.e._ should be as small as possible. For this we use a hash function. If we take this one step further the combination of the signature and the index into the hash table can be seen as different parts of the same hash value. Some bits of this value are used to index into the hash table and some bits are stored in the table. A sketch of this is shown in Figure 2.

Given a fixed amount of memory there is a tradeoff where to put the border between the index part and the signature part. For each bit we take away from

--- end of page.page_number=95 ---

Reducing Memory Usage

84


![](content_assets/paper.pdf-0096-02.png)



![](content_assets/paper.pdf-0096-03.png)



![](content_assets/paper.pdf-0096-04.png)



![](content_assets/paper.pdf-0096-05.png)



![](content_assets/paper.pdf-0096-06.png)



![](content_assets/paper.pdf-0096-07.png)



![](content_assets/paper.pdf-0096-08.png)



![](content_assets/paper.pdf-0096-09.png)



![](content_assets/paper.pdf-0096-10.png)



![](content_assets/paper.pdf-0096-11.png)



![](content_assets/paper.pdf-0096-12.png)



![](content_assets/paper.pdf-0096-13.png)



![](content_assets/paper.pdf-0096-14.png)



![](content_assets/paper.pdf-0096-15.png)



![](content_assets/paper.pdf-0096-16.png)



![](content_assets/paper.pdf-0096-17.png)



![](content_assets/paper.pdf-0096-18.png)



![](content_assets/paper.pdf-0096-19.png)



![](content_assets/paper.pdf-0096-20.png)



![](content_assets/paper.pdf-0096-21.png)



![](content_assets/paper.pdf-0096-22.png)



![](content_assets/paper.pdf-0096-23.png)



![](content_assets/paper.pdf-0096-24.png)


Figure 2: The table index and the signature as one hash value.

the index part we may double the number of bits in the signature, but at the price of less entries in PASSED.

So far we have not mentioned how to handle collisions within the hash table. Since there are now several possible values for the entries in the hash table, it is possible to get collisions in the hash table. Since the main priority of this solution is space, collisions are resolved using open addressing instead of chaining. This will save one pointer for each state entered into PASSED, and since the signatures are, more or less, as big as a pointer we may fit twice as many states in the same amount of memory with open addressing than with chaining. The price we pay for this choice is that the hash table might get full. Normally this would only lead to an expensive rehashing but in our case the information needed to rehash an entry in the hash table is no longer available. This leaves us with two choices, we can either stop the verification and say that PASSED is full and advice the user to try with a larger PASSED, or we can just skip adding the state to PASSED and hope that the search will terminate anyway. In the prototype implementation we have chosen the first alternative.

To evaluate hash compaction for timed automata, we used two slightly different PASSED implementations. The difference between them lies in what we store in the hash table. In the first implementation we store signatures of entire symbolic states. This solution gives a very compact representation of each state in PASSED, but it has the drawback that inclusion between states in PASSED can not be detected. This leads to potentially larger state spaces resulting in a higher pressure on the PASSED structure.

In the second PASSED implementation we try to get around this problem by separating the discrete part and the clock zone. In this implementation we apply the hash function only to the discrete part of the state. The clock zone is compressed using the method from Section 3.3 and stored in the hash table together with the signature. With this solution we aim at minimising the number of states stored in PASSED. However, storing the full zone has a big drawback. The entries in PASSED are much bigger than for the other type. For a fixed

--- end of page.page_number=96 ---

85

Reducing Memory Usage

memory-size this will give less entries in PASSED. A way around this would be to compress the zones further using a method that, with some probability, might report false inclusions. However, this has not been investigated in this paper.

As an introductory experiment all the examples are run with 47-bit signatures[2] for three different sizes of the hash table (16MB, 32MB and 64MB), and an estimate of the covered part of the state space is computed. In order to prevent interference from the inclusion check on WAIT, this feature is turned off. In this experiment we experienced no omissions, but for some examples the verification procedure did not terminate correctly.

The faulty Philips example can not be handled at all by PASSED implementation based only on signatures; while it can be handled by the combined scheme when the size of the passed list is at least 32MB. The reason is that large parts of the state space of this example is revisited since the first PASSED implementation only can detect equal states and not inclusion between states. In contrast to this example, the large instance of the DACAPO example terminates for all sizes using the first PASSED implementation, while it fails to do so for 16MB and 32MB using the second. This is because, for each state, the zone information is an order of magnitude larger than the size of the hash signature. This, in combination with the fact that (for this example) the number of explored states are almost the same in both variations, lead to that 16MB is large enough when using signatures only while 64MB is needed for the combined scheme.

To study what the impact of the signature length on the fraction of the state space that is omitted from exploration we perform an experiment with 7-bit signatures.[3] The result of this experiment can be seen in Table 6. As we see in the table there are still problem instances where no omissions occur. We also note that where omissions occur, in all cases except one, less than one per mille of the state space is omitted from exploration.

As a final experiment we measure the run time and memory use for state space exploration with a PASSED structure based on hash compaction with 47-bit signatures and compare it to the run time for state space exploration using the classic PASSED implementation in UPPAAL. To get as close as possible to a normal use situation, inclusion checking for WAIT is enabled in this experiment. The measured run times are listed in Table 7. We note from the table that the combined scheme (signatures of the discrete part + packed zone) is some-

> 2The size of the signature may seem a little odd, but in the implementation one bit is sacrificed to ensure that no used slot in the hash table can be mistaken for an empty.

> 3This is the smallest possible signature size in the current implementation.

--- end of page.page_number=97 ---

86

Reducing Memory Usage

what faster, for all examples, than using only signatures. The reason for this is the smaller number of states that is visited using the combined scheme. We also note that using hash compaction is somewhat slower than using the classic PASSED implementation (for all examples except Fischers protocol). This is partly due to the extra work needed to compute the signatures and partly due to that the hash compaction implementation within UPPAAL is a prototype.

The measured memory use for the different examples is listed in Table 8. From this table we note that for the large examples, _i.e._ Field Bus, the large DACAPO instance and Fischer 6, there are significant reductions in memory usage. We also note that for some of the smaller examples the classic PASSED implementation use less memory than the hash compaction. This suggests that the chosen size of the hash compaction is too large, and that these examples can be verified using much smaller PASSED. A further observation is that the measured numbers for hash compaction are larger than the requested size for PASSED. The reason for this is that the listed values are the total memory used in the verification, _i.e._ the numbers also include WAIT, temporary storage and the binary code. In a real application, this should be taken into account when deciding how much memory to reserve for PASSED.

## **5 Conclusions**

This paper describes and evaluates three different ways to physically represent symbolic states in PASSED, in implementing verifiers for timed automata. The evaluation shows that if space consumption is a main issue rather than time consumption then the multiply-and-add scheme can be used. For the evaluated examples this optimisation reduces the memory usage by up to 70% compared to the current representation used in UPPAAL, at the price of 3–13 times slowdown due to expensive inclusion checking between states. In all other cases the state should be represented using a mixed representation where the discrete part is represented using the multiply-and-add scheme and the zone is represented by concatenated bit strings separated by test bits. This packing scheme reduces the memory usage with 35%–65% compared to the current version of UPPAAL. In most cases this representation also gives a minor speedup (1%–3%) compared to the current UPPAAL implementation.

Further the paper describes how to improve performance by checking for already visited states not only on PASSED, but also on WAIT. For the evaluated

--- end of page.page_number=98 ---

Reducing Memory Usage

87

|Example|signature|signature+pack|
|---|---|---|
||16MB<br>32MB<br>64MB<br>16MB<br>32MB<br>64MB||
|Philips (correct)|||
|Philips (faulty)|||
|B&O|||
|DACAPO (big)|||
|DACAPO (small)|||
|Fischer 5|||
|Fischer 6|||



Table 6: Fraction of state space (in ) omitted from exploration for hash compaction with 7-bit signatures.

|Example||signature||signature+pack|signature+pack|signature+pack|Classic|
|---|---|---|---|---|---|---|---|
||16MB|32MB|64MB|16MB|32MB|64MB||
|Field Bus (Faulty 1)||||||||
|Field Bus (Faulty 2)||||||||
|Field Bus (Faulty 3)||||||||
|Field Bus (Fixed)||||||||
|Philips (correct)||||||||
|Philips (faulty)||||||||
|B&O||||||||
|DACAPO (big)||||||||
|DACAPO (small)||||||||
|Fischer 5||||||||
|Fischer 6||||||||



Table 7: Run time (in seconds) for state space exploration using a PASSED list based on hash compaction with 47-bit signatures.

|Example|signature|signature+pack|Classic|
|---|---|---|---|
||16MB<br>32MB<br>64MB<br>16MB<br>32MB<br>64MB|||
|Field Bus (Faulty 1)||||
|Field Bus (Faulty 2)||||
|Field Bus (Faulty 3)||||
|Field Bus (Fixed)||||
|Philips (correct)||||
|Philips (faulty)||||
|B&O||||
|DACAPO (big)||||
|DACAPO (small)||||
|Fischer 5||||
|Fischer 6||||



Table 8: Space (in MB) for state space exploration using a PASSED list based on hash compaction with 47-bit signatures.

--- end of page.page_number=99 ---

Reducing Memory Usage

88

examples this optimisation reduces the verification time by up to 85% and the memory usage with up to 45%.

Finally we study PASSED representations based on supertrace and hash compaction effect the performance of UPPAAL. The gain from this technique is significantly reduced memory usage for large examples, but at the price of possibly omitting parts of the state space from exploration. For the evaluated examples a supertrace PASSED cause between 22 per mille and 0.04 per mille of the state space to be omitted from the exploration. The evaluation show also that supertrace PASSED representations only work for examples where the number of revisited states (that can’t be detected without inclusion checking) is small.

For hash compaction we evaluate two, slightly different, methods. One method where a hash key, signature and probe sequence is computed using both the discrete part of the states and the time zone, and one method where the hash key, signature and probe sequence is computed only from the discrete part of the states while the time zone is compressed and stored together with the signature. The evaluation shows that in terms of coverage both these methods outperform the supertrace method. For 47-bit signatures there are no omissions at all (in the evaluated examples) and for 7-bit signatures the number of omissions are less than :th of the number of omissions in the supertrace PASSED representation.

A future extension of this part of the work is to investigate how the size of timing region can be reduced while still maintaining the possibility of inclusion checking between states.

## **References**

- [ABB 01] Tobias Amnell, Gerd Behrmann, Johan Bengtsson, Pedro R. D’Argenio, Alexandre David, Ansgar Fehnker, Thomas Hune, Bertrand Jeannet, Kim G. Larsen, M. Oliver Möller, Paul Pettersson, Carsten Weise, and Wang Yi. UPPAAL - Now, Next, and Future. In _Modelling and Verification of Parallel Processes_ , number 2067 in Lecture Notes in Computer Science, pages 100–125. Springer-Verlag, 2001.

- [AD90] Rajeev Alur and David L. Dill. Automata for modeling real-time systems. In _Proceedings, Seventeenth International Colloquium on Automata, Languages and Programming_ , volume 443 of _Lecture Notes in Computer Science_ , pages 322–335. Springer-Verlag, 1990.

- [AD94] Rajeev Alur and David L. Dill. A theory of timed automata. _Journal of Theoretical Computer Science_ , 126(2):183–235, 1994.

--- end of page.page_number=100 ---

Reducing Memory Usage

89

- [BGK 96] Johan Bengtsson, W. O. David Griffioen, Kåre J. Kristoffersen, Kim G. Larsen, Fredrik Larsson, Paul Petterson, and Wang Yi. Verification of an audio protocol with bus collision using UPPAAL. In _Proceedings, Eigth International Conference on Computer Aided Verification_ , volume 1102 of _Lecture Notes in Computer Science_ . Springer-Verlag, 1996.

- [CW79] J. Lawrence Carter and Mark N. Wegman. Universal classes of hash functions. _Journal of Computer and System Sciences_ , 18(2):143–154, 1979.

- [Dil89] David L. Dill. Timing assumptions and verification of finite-state concurrent systems. In _Proceedings, Automatic Verification Methods for Finite State Systems_ , volume 407 of _Lecture Notes in Computer Science_ , pages 197–212. Springer-Verlag, 1989.

- [DOTY95] Conrado Daws, Alfredo Olivero, Stavros Tripakis, and Sergio Yovine. The tool kronos. In _Proceedings, Hybrid Systems III: Verification and Control_ , volume 1066 of _Lecture Notes in Computer Science_ . Springer-Verlag, 1995.

- [DY00] Alexandre David and Wang Yi. Modelling and analysis of a commercial field bus protocol. In _Proceedings, Twelfth Euromicro Conference on Real Time Systems_ , pages 165–174. IEEE Computer Society Press, 2000.

- [Gra00] Torbjörn Granlund. _The GNU Multiple Precision Arithmetic Library_ , 3.0.1 edition, 2000.

- [HNSY92] Thomas A. Henzinger, Xavier Nicollin, Joseph Sifakis, and Sergio Yovine. Symbolic model checking for real-time systems. In _Proceedings, Seventh Annual IEEE Symposium on Logic in Computer Science_ , pages 394–406, 1992.

- [Hol91] Gerard J. Holzmann. _Design and Validation of Computer Protocols_ . Prentice-Hall, 1991.

- [HSLL97] Klaus Havelund, Arne Skou, Kim G. Larsen, and Kristian Lund. Formal modelling and analysis of an audio/video protocol: An industrial case study using uppaal. In _Proceedings, 18_ th _IEEE Real-Time Systems Symposium_ , pages 2–13. IEEE Computer Society Press, 1997.

- [Lam87] Leslie Lamport. A fast mutual exclusion algorithm. _ACM Transactions on Computer Systems_ , 5(1):1–11, 1987.

- [Lar00] Fredrik Larsson. Efficient implementation of model-checkers for networks of timed automata. Licentiate Thesis 2000-003, Department of Information Technology, Uppsala University, 2000.

- [LP97] Henrik Lönn and Paul Pettersson. Formal verification of a tdma protocol startup mechanism. In _Proceedings of 1997 IEEE Pacific Rim International Symposium on Fault-Tolerant Systems_ , pages 235–242. IEEE Computer Society Press, 1997.

--- end of page.page_number=101 ---

Reducing Memory Usage

90

- [LPY97] Kim G. Larsen, Paul Petterson, and Wang Yi. Uppaal in a nutshell. _Journal on Software Tools for Technology Transfer_ , 1997.

- [Pet99] Paul Pettersson. _Modelling and Verification of Real-Time Systems Using Timed Automata: Theory and Practice_ . PhD thesis, Uppsala University, 1999.

- [PS80] Wolfgang J. Paul and Janos Simon. Decision trees and random access machines. In _Logic and Algorithmic_ , volume 30 of _Monographie de L’Enseignement Mathématique_ , pages 331–340. L’Enseignement Mathématique, Université de Genève, 1980.

- [Rok93] Tomas Gerhard Rokicki. _Representing and Modeling Digital Circuits_ . PhD thesis, Stanford University, 1993.

- [SD95] Ulrich Stern and David L. Dill. Improved probabilistic verification by hash compaction. In _Correct Hardware Design and Verification Methods: IFIP WG10.5 Advanced Research Working Conference Proceedings_ , 1995.

- [WL93] Pierre Wolper and Dennis Leroy. Reliable hashing without collision detection. In _Proceedings, Fifth International Conference on Computer Aided Verification_ , volume 697 of _Lecture Notes in Computer Science_ , pages 59– 70. Springer-Verlag, 1993.

- [Yov97] Sergio Yovine. Kronos: A verification tool for real-time systems. _Journal on Software Tools for Technology Transfer_ , 1, October 1997.

- [YPD94] Wang Yi, Paul Petterson, and Mats Daniels. Automatic verification of realtime communicating systems by constraint-solving. In _Proceedings, Seventh International Conference on Formal Description Techniques_ , pages 223–238, 1994.

--- end of page.page_number=102 ---

Reducing Memory Usage

91

## **A Examples and Experiment Environment**

The experiments are run on a Sun Ultra Enterprise 450 with four[4] 400MHz CPUs and 4GB of main memory. The operating system on the machine was Solaris 7.

All the ideas have been implemented on top of the current development version of UPPAAL (3.1.26), and to measure the performance we used five different applications: Field Bus, B&O, DACAPO, Philips and Fischer. During all the experiments the memory limit for the run is set to 1GB which is at least twice the amount of memory needed for UPPAAL 3.1.26 to check any of the examples, using the standard representation of states. If any run exceeds this limit the run is marked as unsuccessful ( ).

The Field Bus application is a model of the data link layer of a commercial field bus protocol. The protocol and the models we use (three erroneous and one corrected version) are described in [DY00].

B&O is a highly time-sensitive protocol devolved by Bang & Olufsen to transmit control messages between audio/video components. The model used in the experiments is described in [HSLL97].

DACAPO is a model of the start-up algorithm of the so-called DACAPO protocol. The DACAPO protocol is TDMA (time division multiple access) based and intended for local area networks inside modern vehicles. For a more thorough description of this application, see [LP97]. In these experiments we use two different models: a small one with three stations and drifting clocks, and larger one with four stations and perfect clocks.

The Philips example is a model of the physical layer of a protocol used by Philips to connect different parts of stereo equipment. This model was one of the first larger case studies made with UPPAAL. The model is thoroughly described in [BGK 96]. This example is only used in the experiments with probabilistic passed lists. Two versions of this protocol are used in the experiments, the correct model and one faulty model.

The last application is Fischers protocol for mutual exclusion [Lam87]. This simple protocol for mutual exclusion has, unfortunately, become a standard benchmark for verification tools for timed systems, since the state space grows rapidly with the number of processes. The reason that this example is not a good

> 4 The version of UPPAAL used in the experiments is not multi threaded, so we only use one CPU for each run.

--- end of page.page_number=103 ---

Reducing Memory Usage

92

benchmark example is that it is not very realistic and it behaves differently, verification-wise, from examples based on real case studies. In the experiments we have used two different sizes of this problem, one with five processes and one with six processes.

--- end of page.page_number=104 ---

## **Paper D:**

## **Partial Order Reductions for Timed Systems**

Johan Bengtsson, Bengt Jonsson, Johan Lilius and Wang Yi.

--- end of page.page_number=105 ---

--- end of page.page_number=106 ---

95

Partial Order Reductions for Timed Systems

## **Partial Order Reductions for Timed Systems**

Johan Bengtsson Bengt Jonsson Johan Lilius Wang Yi

Department of Computer Systems, Uppsala University, Sweden. Email: {bengt,johanb,yi}@docs.uu.se Department of Computer Science, TUCS, Åbo Akademi University, Finland. Email: Johan.Lilius@abo.fi

**Abstract.** In this paper, we present a partial-order reduction method for timed systems based on a local-time semantics for networks of timed automata. The main idea is to remove the implicit clock synchronisation between processes in a network by letting local clocks in each process advance independently of clocks in other processes, and by requiring that two processes resynchronise their local time scales whenever they communicate. A symbolic version of this new semantics is developed in terms of predicate transformers, which enjoys the desired property that two predicate transformers are independent if they correspond to disjoint transitions in different processes. Thus we can apply standard partial order reduction techniques to the problem of checking reachability for timed systems, which avoid exploration of unnecessary interleavings of independent transitions. The price is that we must introduce extra machinery to perform the resynchronisation operations on local clocks. Finally, we present a variant of DBM representation of symbolic states in the local time semantics for efficient implementation of our method.

## **1 Motivation**

During the past few years, a number of verification tools have been developed for timed systems in the framework of timed automata (e.g. KRONOS and UPPAAL) [HH95, DOTY95, BLL 96]. One of the major problems in applying these tools to industrial-size systems is the huge memory-usage (e.g. [BGK 96]) needed to explore the state-space of a network (or product) of timed automata, since the verification tools must keep information not only on the control structure of the automata but also on the clock values specified by clock constraints.

Partial-order reduction (e.g., [God96, GW90, HP94, Pel93, Val90, Val93]) is a well developed technique, whose purpose is to reduce the usage of time and memory in state-space exploration by avoiding to explore unnecessary inter-

--- end of page.page_number=107 ---

Partial Order Reductions for Timed Systems

96

leavings of independent transitions. It has been successfully applied to finitestate systems. However, for timed systems there has been less progress. Perhaps the major obstacle to the application of partial order reduction to timed systems is the assumption that all clocks advance at the same speed, meaning that all clocks are implicitly synchronised. If each process contains (at least) one local clock, this means that advancement of the local clock of a process is not independent of time advancements in other processes. Therefore, different interleavings of a set of independent transitions will produce different combinations of clock values, even if there is no explicit synchronisation between the processes or their clocks.

A simple illustration of this problem is given in Figure 1. In (1) of Figure 1 is a system with two automata, each of which can perform one internal local transition ( and respectively) from an initial local state to a synchronisation state where the automata may synchronise on label (we use the synchronisation model of CCS). It is clear that the two sequences of transitions and are different interleavings of two independent transitions, both leading to the state , from which a synchronisation on is possible. A partial order reduction technique will explore only one of these two interleavings, after having analysed that the initial transitions of the two automata are independent.


![](content_assets/paper.pdf-0108-04.png)



![](content_assets/paper.pdf-0108-05.png)



![](content_assets/paper.pdf-0108-06.png)



![](content_assets/paper.pdf-0108-07.png)



![](content_assets/paper.pdf-0108-08.png)



![](content_assets/paper.pdf-0108-09.png)


Figure 1: Illustration of Partial Order Reduction

Let us now introduce timing constraints in terms of clocks into the example, to obtain the system in (2) of Figure 1 where we add clocks and . The left automaton can initially move to node , thereby resetting the clock , after waiting an arbitrary time. Thereafter it can move to node after more than time units. The right automaton can initially move to node , thereby resetting the clock , after waiting an arbitrary time. Thereafter it can move to node within time units, but within 10 time units of initialisation of the

--- end of page.page_number=108 ---

Partial Order Reductions for Timed Systems

97

system. We note that the initial transitions of the two automata are logically independent of each other. However, if we naively analyse the possible values of clocks after a certain sequence of actions, we find that the sequence may result in clock values that satisfy (as is reset before ) where the synchronisation on is possible, whereas the sequence may result in clock values that satisfy (as is reset after ) where the synchronisation on is impossible. Now, we see that it is in general not sufficient to explore only one interleaving of independent transitions.

In this paper, we present a new method for partial order reductions for timed systems based on a new local-time semantics for networks of timed automata. The main idea is to overcome the problem illustrated in the previous example by removing the implicit clock synchronisation between processes by letting clocks advance independently of each other. In other words, we desynchronise local clocks. The benefit is that different interleavings of independent transitions will no longer remember the order in which the transitions were explored. In this specific example, an interleaving will not “remember” the order in which the clocks were reset, and the two initial transitions are independent. We can then import standard partial order techniques, and expect to get the same reductions as in the untimed case. We again illustrate this on system (2) of Figure 1. Suppose that in state all clocks are initialised to . In the standard semantics, the possible clock values when the system is in state are those that satisfy . In the “desynchronised” semantics presented in this paper, any combination of clock values is possible in state . After both the sequence and the possible clock values are those that satisfy .

Note that the desynchronisation will give rise to many new global states in which automata have “executed” for different amounts of time. We hope that this larger set of states can be represented symbolically more compactly than the original state-space. For example, in system (2), our desynchronised semantics gives rise to the constraint at state , whereas the standard semantics gives rise to the two constraints and . However, as we have removed the synchronisation between local time scales completely, we also lose timing information required for synchronisation between automata. Consider again system (2) and look at the clock of the right automaton. Since initially, the constraint requires that the synchronisation on should be within time units from system initialisation. Implicitly, this then becomes a requirement on the left automaton. A naive desynchronisation of lo-

--- end of page.page_number=109 ---

Partial Order Reductions for Timed Systems

98

cal clocks including will allow the left process to wait for more than time units, in its local time scale, before synchronising. Therefore, before exploring the effect of a transition in which two automata synchronise, we must explicitly “resynchronise” the local time scales of the participating automata. For this purpose, we add to each automaton a local reference clock, which measures how far its local time has advanced in performing local transitions. To each synchronisation between two automata, we add the condition that their reference clocks agree. In the above example, we add as a reference clock to the left automaton and as a reference clock to the right automaton. We require at system initialisation. After any interleaving of the first two independent transitions, the clock values may satisfy and . To synchronise on they must also satisfy the constraint in addition to , and . This implies that when the synchronisation occurs. Without the reference clocks, we would not have been able to derive this condition.

The idea of introducing local time is related to the treatment of local time in the field of parallel simulation (e.g., [Fuj90]). Here, a simulation step involves some local computation of a process together with a corresponding update of its local time. A snapshot of the system state during a simulation will be composed of many local time scales. In our work, we are concerned with verification rather than simulation, and we must therefore represent sets of such system states symbolically. We shall develop a symbolic version for the local-time semantics in terms of predicate transformers, in analogy with the ordinary symbolic semantics for timed automata, which is used in several tools for reachability analysis. The symbolic semantics allows a finite partitioning of the state space of a network and enjoys the desired property that two predicate transformers are independent if they correspond to disjoint transitions in different component automata. Thus we can apply standard partial order reduction techniques to the problem of checking reachability for timed systems, without disturbance from implicit synchronisation of clocks.

The paper is organised as follows: In section 2, we give a brief introduction to the notion of timed automata and its standard semantics i.e. the global time semantics. Section 3 develops a local time semantics for networks of timed automata and a finite symbolic version of the new semantics, analogous to the region graph for timed automata. Section 4 presents a partial order search algorithm for reachability analysis based on the symbolic local time semantics; together with necessary operations to represent and manipulate distributed symbolic states. Section 5 concludes the paper with a short summary on related work, our contribution and future work.

--- end of page.page_number=110 ---

Partial Order Reductions for Timed Systems

99

## **2 Preliminaries**

## **2.1 Networks of Timed Automata**

Timed automata was first introduced in [AD90] and has since then established itself as a standard model for timed systems. For the reader not familiar with the notion of timed automata we give a short informal description. In this paper, we will work with networks of timed automata [YPD94, LPY95] as the model for timed systems.

Let be a finite set of labels ranged over by etc. Each label is either local or synchronising. If is a synchronising label, then it has a complement, denoted , which is also a synchronising label with .

A timed automaton is a standard finite–state automaton over alphabet , extended with a finite collection of real–valued clocks to model timing. We use etc. to range over clocks, and etc. to range over finite sets of clocks, and **R** to stand for the set of non-negative real numbers.

A clock assignment for a set of clocks is a function from to **R** . For **R** , we use to denote the clock assignment which maps each clock in to the value and for , to denote the assignment for which maps each clock in to the value and agrees with on .

We use ranged over by (and later by ), to stand for the set of conjunctions of atomic constraints of the form: or for , and being a natural number. Elements of are called clock constraints or clock constraint systems over . We use to denote that the clock assignment **R** satisfies the clock constraint .

A network of timed automata is the parallel composition of a collection of timed automata. Each is a timed automaton over the clocks , represented as a tuple , where is a finite set of (control) nodes, is the initial node, and is a set of edges. Each edge means that the automaton can move from the node to the node if the clock constraint (also called the enabling condition of the edge) is satisfied, thereby performing the label and resetting the clocks in . We write for . A local action is an edge of some automaton with a local label . A synchronising action is a pair of matching edges, written where is a synchronising label, and for some , is an edge of

--- end of page.page_number=111 ---

Partial Order Reductions for Timed Systems

100


![](content_assets/paper.pdf-0112-02.png)



![](content_assets/paper.pdf-0112-03.png)


and is an edge of . The assigns to each node an invariant condition which must be satisfied by the system clocks whenever the system is operating in that node. For simplicity, we require that the invariant conditions of timed automata should be the conjunction of constraints in the form: where is a clock and is a natural number. We require the sets to be pairwise disjoint, so that each automaton only references local clocks. As a technical convenience, we assume that the sets of nodes are pairwise disjoint.

## **Global Time Semantics.**

A state of a network is a pair where , called a control vector, is a vector of control nodes of each automaton, and is a clock assignment for . We shall use to stand for the th element of and for the control vector where the th element of is replaced by . We define the invariant of as the conjunction . The initial state of is where is the control vector such that for each , and maps all clocks in to .

A network may change its state by performing the following three types of transitions.


![](content_assets/paper.pdf-0112-08.png)



![](content_assets/paper.pdf-0112-09.png)



![](content_assets/paper.pdf-0112-10.png)


Delay Transition: if


![](content_assets/paper.pdf-0112-12.png)



![](content_assets/paper.pdf-0112-13.png)



![](content_assets/paper.pdf-0112-14.png)


Local Transition: if there exists a local action such that and .


![](content_assets/paper.pdf-0112-16.png)



![](content_assets/paper.pdf-0112-17.png)



![](content_assets/paper.pdf-0112-18.png)



![](content_assets/paper.pdf-0112-19.png)



![](content_assets/paper.pdf-0112-20.png)


Synchronising Transition: if there exists a synchronising action such that , , and .

We shall say that a state is reachable, denoted if there exists a sequence of (delay or discrete) transitions leading from to .

## **2.2 Symbolic Global–Time Semantics**

Clearly, the semantics of a timed automaton yields an infinite transition system, and is thus not an appropriate basis for verification algorithms. However, efficient algorithms may be obtained using a symbolic semantics based on symbolic states of the form , where , which represent the set of

--- end of page.page_number=112 ---

Partial Order Reductions for Timed Systems

101

states such that . Let us write to denote that and .

We perform symbolic state space exploration by repeatedly taking the strongest postcondition with respect to an action, or to time advancement. For a constraint and set of clocks, define the constraints and by


![](content_assets/paper.pdf-0113-04.png)



![](content_assets/paper.pdf-0113-05.png)


for all **R** we have iff , and

iff


![](content_assets/paper.pdf-0113-08.png)



![](content_assets/paper.pdf-0113-09.png)



![](content_assets/paper.pdf-0113-10.png)



![](content_assets/paper.pdf-0113-11.png)



![](content_assets/paper.pdf-0113-12.png)



![](content_assets/paper.pdf-0113-13.png)



![](content_assets/paper.pdf-0113-14.png)



![](content_assets/paper.pdf-0113-15.png)


It can be shown that and can be expressed as clock constraints whenever is a clock constraint. We now define predicate transformers corresponding to strongest postconditions of the three types of transitions:


![](content_assets/paper.pdf-0113-17.png)



![](content_assets/paper.pdf-0113-18.png)



![](content_assets/paper.pdf-0113-19.png)



![](content_assets/paper.pdf-0113-20.png)



![](content_assets/paper.pdf-0113-21.png)



![](content_assets/paper.pdf-0113-22.png)



![](content_assets/paper.pdf-0113-23.png)



![](content_assets/paper.pdf-0113-24.png)



![](content_assets/paper.pdf-0113-25.png)



![](content_assets/paper.pdf-0113-26.png)


For global delay,


![](content_assets/paper.pdf-0113-28.png)



![](content_assets/paper.pdf-0113-29.png)



![](content_assets/paper.pdf-0113-30.png)



![](content_assets/paper.pdf-0113-31.png)



![](content_assets/paper.pdf-0113-32.png)



![](content_assets/paper.pdf-0113-33.png)



![](content_assets/paper.pdf-0113-34.png)



![](content_assets/paper.pdf-0113-35.png)



![](content_assets/paper.pdf-0113-36.png)



![](content_assets/paper.pdf-0113-37.png)



![](content_assets/paper.pdf-0113-38.png)



![](content_assets/paper.pdf-0113-39.png)


For a local action ,


![](content_assets/paper.pdf-0113-41.png)



![](content_assets/paper.pdf-0113-42.png)



![](content_assets/paper.pdf-0113-43.png)



![](content_assets/paper.pdf-0113-44.png)



![](content_assets/paper.pdf-0113-45.png)



![](content_assets/paper.pdf-0113-46.png)


For a synchronising action ,


![](content_assets/paper.pdf-0113-48.png)



![](content_assets/paper.pdf-0113-49.png)



![](content_assets/paper.pdf-0113-50.png)



![](content_assets/paper.pdf-0113-51.png)



![](content_assets/paper.pdf-0113-52.png)



![](content_assets/paper.pdf-0113-53.png)



![](content_assets/paper.pdf-0113-54.png)



![](content_assets/paper.pdf-0113-55.png)



![](content_assets/paper.pdf-0113-56.png)



![](content_assets/paper.pdf-0113-57.png)



![](content_assets/paper.pdf-0113-58.png)



![](content_assets/paper.pdf-0113-59.png)



![](content_assets/paper.pdf-0113-60.png)



![](content_assets/paper.pdf-0113-61.png)



![](content_assets/paper.pdf-0113-62.png)



![](content_assets/paper.pdf-0113-63.png)



![](content_assets/paper.pdf-0113-64.png)



![](content_assets/paper.pdf-0113-65.png)



![](content_assets/paper.pdf-0113-66.png)



![](content_assets/paper.pdf-0113-67.png)



![](content_assets/paper.pdf-0113-68.png)



![](content_assets/paper.pdf-0113-69.png)



![](content_assets/paper.pdf-0113-70.png)



![](content_assets/paper.pdf-0113-71.png)



![](content_assets/paper.pdf-0113-72.png)



![](content_assets/paper.pdf-0113-73.png)



![](content_assets/paper.pdf-0113-74.png)



![](content_assets/paper.pdf-0113-75.png)



![](content_assets/paper.pdf-0113-76.png)



![](content_assets/paper.pdf-0113-77.png)



![](content_assets/paper.pdf-0113-78.png)



![](content_assets/paper.pdf-0113-79.png)



![](content_assets/paper.pdf-0113-80.png)



![](content_assets/paper.pdf-0113-81.png)



![](content_assets/paper.pdf-0113-82.png)



![](content_assets/paper.pdf-0113-83.png)



![](content_assets/paper.pdf-0113-84.png)



![](content_assets/paper.pdf-0113-85.png)



![](content_assets/paper.pdf-0113-86.png)


It turns out to be convenient to use predicate transformers that correspond to first executing a discrete action, and thereafter executing a delay. For predicate transformers , we use to denote the composition . For a (local or synchronising) action , we define .

From now on, we shall use to denote the initial symbolic global time state for networks, where . We write if for some action . It can be shown (e.g. [YPD94]) that the symbolic semantics characterises the concrete semantics given earlier in the following sense:

**Theorem 1** _A state of a network is reachable if and only if for some such that ._


![](content_assets/paper.pdf-0113-90.png)



![](content_assets/paper.pdf-0113-91.png)



![](content_assets/paper.pdf-0113-92.png)



![](content_assets/paper.pdf-0113-93.png)



![](content_assets/paper.pdf-0113-94.png)


The above theorem can be used to construct a symbolic algorithm for reachability analysis. In order to keep the presentation simple, we will in the rest of the paper only consider a special form of local reachability, defined as follows. Given a control node of some automaton , check if there is a reachable state such that . It is straight-forward to extend our results to more general reachability problems. The symbolic algorithm for checking local

--- end of page.page_number=113 ---

Partial Order Reductions for Timed Systems

102


![](content_assets/paper.pdf-0114-02.png)


Figure 2: An Algorithm for Symbolic Reachability Analysis.

reachability is shown in Figure 2 for a network of timed automata. Here, the set denotes the set of all actions whose source node(s) are in the control vector i.e., a local action is enabled at if , and a synchronising action is enabled at if and .

## **3 Partial Order Reduction and Local-Time Semantics**

The purpose of partial-order techniques is to avoid exploring several interleavings of independent transitions, i.e., transitions whose order of execution is irrelevant, e.g., because they are performed by different processes and do not affect each other. Assume for instance that for some control vector , the set consists of the local action of automaton and the local action of automaton . Since executions of local actions do not affect each other, we might want to explore only the action , and defer the exploration of until later. The justification for deferring to explore would be that any symbolic state which is reached by first exploring and thereafter can also be reached by exploring these actions in reverse order, i.e., first and thereafter .

--- end of page.page_number=114 ---

Partial Order Reductions for Timed Systems

103

Let and be two predicate transformers. We say that and are independent if for any symbolic state . In the absence of time, local actions of different processes are independent, in the sense that and are independent. However, in the presence of time, we do not have independence. That is, and are in general not independent, as illustrated e.g., by the example in Figure 1.

If timed predicate transformers commute only to a rather limited extent, then partial order reduction is less likely to be successful for timed systems than for untimed systems. In this paper, we present a method for symbolic state-space exploration of timed systems, in which predicate transformers commute to the same extent as they do in untimed systems. The main obstacle for commutativity of timed predicate transformers is that timed advancement is modelled by globally synchronous transitions, which implicitly synchronise all local clocks, and hence all processes. In our approach, we propose to replace the global timeadvancement steps by local-time advancement. In other words, we remove the constraint that all clocks advance at the same speed and let clocks of each automaton advance totally independently of each other. We thus replace one global time scale by a local-time scale for each automaton. When exploring local actions, the corresponding predicate transformer affects only the clocks of that automaton in its local-time scale; the clocks of other automata are unaffected. In this way, we have removed any relation between local-time scales. However, in order to explore pairs of synchronising actions we must also be able to “resynchronise” the local-time scales of the participating automata, and for this purpose we add a local reference clock to each automaton. The reference clock of automaton represents how far the local-time of has advanced, measured in a global time scale. In a totally unsynchronised state, the reference clocks of different automata can be quite different. Before a synchronisation between and , we must add the condition that the reference clocks of and are equal.

To formalise the above ideas further, we present a local-time semantics for networks of timed automata, which allows local clocks to advance independently and resynchronising them only at synchronisation points.

Consider a network . We add to the set of clocks of each a reference clock, denoted . Let us denote by the time assignment which maps each clock in (including ) to the value and each clock in to the value . In the rest of the paper, we shall assume that the set of clocks of a network include the reference clocks and the initial state is

--- end of page.page_number=115 ---

Partial Order Reductions for Timed Systems

104

where the reference clock values are , in both the global and local time semantics.

## **Local Time Semantics.**

The following rules define that networks may change their state locally and globally by performing three types of transitions:


![](content_assets/paper.pdf-0116-05.png)



![](content_assets/paper.pdf-0116-06.png)



![](content_assets/paper.pdf-0116-07.png)



![](content_assets/paper.pdf-0116-08.png)


Local Delay Transition:

- if


![](content_assets/paper.pdf-0116-11.png)



![](content_assets/paper.pdf-0116-12.png)



![](content_assets/paper.pdf-0116-13.png)



![](content_assets/paper.pdf-0116-14.png)



![](content_assets/paper.pdf-0116-15.png)



![](content_assets/paper.pdf-0116-16.png)



![](content_assets/paper.pdf-0116-17.png)


- Local Discrete Transition: if there exists a local action such that and


![](content_assets/paper.pdf-0116-19.png)


- Synchronising Transition: if there exists a synchronising action such that , , and , and

Intuitively, the first rule says that a component may advance its local clocks (or execute) as long as the local invariant holds. The second rule is the standard interleaving rule for discrete transitions. When two components need to synchronise, it must be checked if they have executed for the same amount of time. This is specified by the last condition of the third rule which states that the local reference clocks must agree, i.e. .

We call a local time state. Obviously, according to the above rules, a network may reach a large number of local time states where the reference clocks take different values. To an external observer, the interesting states of a network will be those where all the reference clocks take the same value.

**Definition 1** _A local time state with reference clocks is_ synchronised _if ._

Now we claim that the local-time semantics simulates the standard global time semantics in which local clocks advance concurrently, in the sense that they can generate precisely the same set of reachable states of a timed system.

**Theorem 2** _For all networks, iff for all synchronised local time states ._

## **3.1 Symbolic Local-Time Semantics**

We can now define a local-time analogue of the symbolic semantics given in Section 2.2 to develop a symbolic reachability algorithm with partial order

--- end of page.page_number=116 ---

105

Partial Order Reductions for Timed Systems

reduction. We need to represent local time states by constraints. Let us first assume that the constraints we need for denote symbolic local time states are different from standard clock constraints, and use etc to denote such constraints. Later, we will show that such constraints can be expressed as a clock constraint.

We use to denote the clock constraint such that for all **R** we have iff . For local-time advance, we define a local-time predicate transformer, denoted , which allows only the local clocks including the reference clock to advance as follows:


![](content_assets/paper.pdf-0117-04.png)



![](content_assets/paper.pdf-0117-05.png)



![](content_assets/paper.pdf-0117-06.png)



![](content_assets/paper.pdf-0117-07.png)



![](content_assets/paper.pdf-0117-08.png)



![](content_assets/paper.pdf-0117-09.png)



![](content_assets/paper.pdf-0117-10.png)



![](content_assets/paper.pdf-0117-11.png)



![](content_assets/paper.pdf-0117-12.png)



![](content_assets/paper.pdf-0117-13.png)



![](content_assets/paper.pdf-0117-14.png)



![](content_assets/paper.pdf-0117-15.png)



![](content_assets/paper.pdf-0117-16.png)



![](content_assets/paper.pdf-0117-17.png)


For each local and synchronising action , we define a local-time predicate transformer, denoted , as follows:


![](content_assets/paper.pdf-0117-19.png)



![](content_assets/paper.pdf-0117-20.png)



![](content_assets/paper.pdf-0117-21.png)



![](content_assets/paper.pdf-0117-22.png)



![](content_assets/paper.pdf-0117-23.png)


If is a local action , then


![](content_assets/paper.pdf-0117-25.png)



![](content_assets/paper.pdf-0117-26.png)



![](content_assets/paper.pdf-0117-27.png)



![](content_assets/paper.pdf-0117-28.png)



![](content_assets/paper.pdf-0117-29.png)



![](content_assets/paper.pdf-0117-30.png)



![](content_assets/paper.pdf-0117-31.png)



![](content_assets/paper.pdf-0117-32.png)



![](content_assets/paper.pdf-0117-33.png)



![](content_assets/paper.pdf-0117-34.png)


If is a synchronising action , then


![](content_assets/paper.pdf-0117-36.png)



![](content_assets/paper.pdf-0117-37.png)



![](content_assets/paper.pdf-0117-38.png)



![](content_assets/paper.pdf-0117-39.png)



![](content_assets/paper.pdf-0117-40.png)



![](content_assets/paper.pdf-0117-41.png)



![](content_assets/paper.pdf-0117-42.png)



![](content_assets/paper.pdf-0117-43.png)



![](content_assets/paper.pdf-0117-44.png)



![](content_assets/paper.pdf-0117-45.png)



![](content_assets/paper.pdf-0117-46.png)



![](content_assets/paper.pdf-0117-47.png)



![](content_assets/paper.pdf-0117-48.png)



![](content_assets/paper.pdf-0117-49.png)



![](content_assets/paper.pdf-0117-50.png)



![](content_assets/paper.pdf-0117-51.png)



![](content_assets/paper.pdf-0117-52.png)



![](content_assets/paper.pdf-0117-53.png)



![](content_assets/paper.pdf-0117-54.png)



![](content_assets/paper.pdf-0117-55.png)



![](content_assets/paper.pdf-0117-56.png)



![](content_assets/paper.pdf-0117-57.png)


Note that in the last definition, we treat a clock constraint like as a predicate transformer, defined in the natural way by


![](content_assets/paper.pdf-0117-59.png)



![](content_assets/paper.pdf-0117-60.png)



![](content_assets/paper.pdf-0117-61.png)


.

We use to denote the initial symbolic local time state of networks where . We shall write if for some action .

Then we have the following characterisation theorem.

**Theorem 3** _For all networks, a synchronised state , if and only if for a symbolic local time state such that ._

The above theorem shows that the symbolic local time semantics fully characterises the global time semantics in terms of reachable states. Thus we can perform reachability analysis in terms of the symbolic local time semantics. However, it requires to find a symbolic local time state that is synchronised in the sense that it contains synchronised states. The searching for such a synchronised symbolic state may be time and space-consuming. Now, we relax the condition for a class of networks, namely those containing no local time-stop.

--- end of page.page_number=117 ---

Partial Order Reductions for Timed Systems

106

**Definition 2** _A network is local time-stop free if for all , implies for some synchronised state ._


![](content_assets/paper.pdf-0118-03.png)



![](content_assets/paper.pdf-0118-04.png)



![](content_assets/paper.pdf-0118-05.png)



![](content_assets/paper.pdf-0118-06.png)



![](content_assets/paper.pdf-0118-07.png)



![](content_assets/paper.pdf-0118-08.png)


The local time-stop freeness can be easily guaranteed by syntactical restriction on component automata of networks. For example, we may require that at each control node of an automaton there should be an edge with a local label and a guard weaker than the local invariant. This is precisely the way of modelling time-out handling at each node when the invariant is becoming false and therefore it is a natural restriction.

The following theorem allows us to perform reachability analysis in terms of symbolic local time semantics for local time-stop free networks without searching for synchronised symbolic states.

**Theorem 4** _Assume a local time-stop free network and a local control node of . Then for some such that if and only if for some such that ._

We now state that the version of the timed predicate transformers based on local time semantics enjoy the commutativity properties that were missing in the global time approach.

**Theorem 5** _Let and be two actions of a network of timed automata. If the sets of component automata of involved in and are disjoint, then and are independent._

## **3.2 Finiteness of the Symbolic Local Time Semantics**

We shall use the symbolic local time semantics as the basis to develop a partial order search algorithm in the following section. To guarantee termination of the algorithm, we need to establish the finiteness of our local time semantics, i.e. that the number of equivalent symbolic states is finite. Observe that the number of symbolic local time states is in general infinite. However, we can show that there is finite partitioning of the state space. We take the same approach as for standard timed automata, that is, we construct a finite graph based on a notion of regions.

We first extend the standard region equivalence to synchronised states. In the following we shall use to denote the set of reference clocks.

--- end of page.page_number=118 ---

Partial Order Reductions for Timed Systems

107

**Definition 3** _Two synchronised local time states (with the same control vector) and are synchronised-equivalent if where is the standard region equivalence for timed automata._

Note that means that only the non-reference clock values in and are region-equivalent. We call the equivalence classes w.r.t. the above equivalence relation synchronised regions. Now we extend this relation to cope with local time states that are not synchronised. Intuitively, we want two non-synchronised states, and to be classified as equivalent if they can reach sets of equivalent synchronised states just by letting the automata that have lower reference clock values advance to catch up with the automaton with the highest reference clock value.

**Definition 4** _A local delay transition of a network is a_ catch-up transition _if ._

Intuitively a catch-up transition corresponds to running one of the automata that lags behind, and thus making the system more synchronised in time.

**Definition 5** _Let be a local time state of a network of timed automata. We use to denote the set of synchronised regions reachable from only by discrete transitions or catch-up transitions._

We now define an equivalence relation between local time states.

**Definition 6** _Two local time states and are_ catch-up equivalent _denoted if . We shall use to denote the equivalence class of local time states w.r.t. ._

Intuitively two catch-up equivalent local time states can reach the same set of synchronised states i.e. states where all the automata of the network have been synchronised in time.

Note that the number of synchronised regions is finite. This implies that the number of catch-up classes is also finite. On the other hand, there is no way to put an upper bound on the reference clocks , since that would imply that for every process there is a point in time where it stops evolving which is generally not the case. This leads to the conclusion that there must be a periodicity in the region graph, perhaps after some initial steps. Nevertheless, we have a finiteness theorem.

**Theorem 6** _For any network of timed automata, the number of catch-up equivalence classes for each vector of control nodes is bounded by a func-_

--- end of page.page_number=119 ---

Partial Order Reductions for Timed Systems

108

_tion of the number of regions in the standard region graph construction for timed automata._

As the number of vectors of control nodes for each network of automata is finite, the above theorem demonstrates the finiteness of our symbolic local time semantics.

## **4 Partial Order Reduction in Reachability Analysis**

The preceding sections have developed the necessary machinery for presenting a method for partial-order reduction in a symbolic reachability algorithm. Such an algorithm can be obtained from the algorithm in Figure 2 by replacing the initial symbolic global time state by the initial symbolic local time state (as defined in Theorem 4), and by replacing the statement


![](content_assets/paper.pdf-0120-06.png)


SUCC:=


![](content_assets/paper.pdf-0120-08.png)



![](content_assets/paper.pdf-0120-09.png)



![](content_assets/paper.pdf-0120-10.png)



![](content_assets/paper.pdf-0120-11.png)



![](content_assets/paper.pdf-0120-12.png)



![](content_assets/paper.pdf-0120-13.png)



![](content_assets/paper.pdf-0120-14.png)



![](content_assets/paper.pdf-0120-15.png)



![](content_assets/paper.pdf-0120-16.png)



![](content_assets/paper.pdf-0120-17.png)



![](content_assets/paper.pdf-0120-18.png)



![](content_assets/paper.pdf-0120-19.png)



![](content_assets/paper.pdf-0120-20.png)


by SUCC:= where is a subset of the actions that are enabled at . Hopefully the set can be made significantly smaller than , leading to a reduction in the explored symbolic state-space.

In the literature on partial order reduction, there are several criteria for choosing the set so that the reachability analysis is still complete. We note that our setup would work with any criterion which is based on the notion of “independent actions” or “independent predicate transformers”. A natural criterion which seems to fit our framework was first formulated by Overman [Ove81]; we use its formulation by Godefroid [God96].

The idea in this reduction is that for each control vector we choose a subset of the automata , and let be all enabled actions in which the automata in participate. The choice of may depend on the control node that we are searching for. The set must satisfy the criteria below. Note that the conditions are formulated only in terms of the control structure of the automata. Note also that in an implementation, these conditions will be replaced by conditions that are easier to check (e.g. [God96]).

C0 if and only if .

- C1 If the automaton from its current node can possibly synchronise with another process , then , regardless of whether such a synchronisation is enabled or not.

--- end of page.page_number=120 ---

Partial Order Reductions for Timed Systems

109

- C2 From , the network cannot reach a control vector with without performing an action in which some process in participates.

Criteria **C0** and **C2** are obviously necessary to preserve correctness. Criterion **C1** can be intuitively motivated as follows: If automaton can possibly synchronise with another automaton , then we must explore actions by to allow it to “catch up” to a possible synchronisation with . Otherwise we may miss to explore the part of the state-space that can be reached after the synchronisation between and .

A final necessary criterion for correctness is fairness, i.e., that we must not indefinitely neglect actions of some automaton. Otherwise we may get stuck exploring a cyclic behaviour of a subset of the automata. This criterion can be formulated in terms of the global control graph of the network. Intuitively, this graph has control vectors as nodes, which are connected by symbolic transitions where the clock constraints are ignored. The criterion of fairness then requires that

- C3 In each cycle of the global control graph, there must be at least one control vector at which .

In the following theorem, we state correctness of our criteria.

**Theorem 7** _A partial order reduction of the symbolic reachability in Figure 2, obtained by replacing_

_1. the initial symbolic global time state with the initial symbolic local time state (as defined in theorem 4)_

_2. the statement_ SUCC _:= with the statement_ SUCC _:= where the function satisfies the criteria_ **C0** _-_ **C3** _,_

_3. and finally the inclusion checking i.e. between constraints with an inclusion checking that also takes into account_[1] _._

_is a correct and complete decision procedure for determining whether a local state in is reachable in a local time-stop free network ._

The proof of the above theorem follows similar lines as other standard proofs of correctness for partial order algorithms. See e.g., [God96].

1This last change is only to guarantee the termination but not the soundness of the algorithm. Note that in this paper, we have only shown that there exists a finite partition of the local time state space according to , but not how the partitioning should be done. This is our future work.

--- end of page.page_number=121 ---

Partial Order Reductions for Timed Systems

110

## **4.1 Operations on Constraint Systems**

Finally, to develop an efficient implementation of the search algorithm presented above, it is important to design efficient data structures and algorithms for the representation and manipulation of symbolic distributed states i.e. constraints over local clocks including the reference clocks.

In the standard approach to verification of timed systems, one such well-known data structure is the Difference Bound Matrix (DBM), due to Bellman [Bel57], which offers a canonical representation for clock constraints. Various efficient algorithms to manipulate (and analyse) DBM’s have been developed (see e.g [LLPY97]).

However when we introduce operations of the form , the standard clock constraints are no longer adequate for describing possible sets of clock assignments, because it is not possible to let only a subset of the clocks grow. This problem can be circumvented by the following. Instead of considering values of clocks as the basic entity in a clock constraint, we work in terms of the relative offset of a clock from the local reference clock. For a clock , this offset is represented by the difference . By analogy, we must introduce the constant offset . An offset constraint is then a conjunction of inequalities of form or for , where . Note that an inequality of the form is also an offset, since it is the same as . It is important to notice, that given an offset constraint we can always recover the absolute constraint by setting .

The nice feature of these constraints is that they can be represented by DBM’s, by changing the interpretation of a clock from being its value to being its local offset. Thus given a set of offset constraints over a , we construct a DBM as follows. We number the clocks in by . An offset of the form we denote by and a constant offset by . The index set of the matrix is then the set of offsets and for for all , while an entry in M is defined by if and otherwise. We say that a clock assignment is a solution of a DBM , , iff , where with the reference clock of .

The operation now corresponds to the deletion of all constraints of the form . The intuition behind this is that when we let the clocks in grow, we are keeping the relative offsets constant, and only the clock will decrease,

--- end of page.page_number=122 ---

Partial Order Reductions for Timed Systems

111

because this offset is taken from 0. can be defined as an operation on the corresponding DBM : if and otherwise. It then easy to see that iff .

Resetting of a clock corresponds to the deletion of all constraints regarding and then setting . This can be done by an operation if and or and , if and or and , and otherwise. Again it is easy to see, that iff .

## **5 Conclusion and Related Work**

In this paper, we have presented a partial-order reduction method for timed systems, based on a local-time semantics for networks of timed automata. We have developed a symbolic version of this new (local time) semantics in terms of predicate transformers, in analogy with the ordinary symbolic semantics for timed automata which is used in current tools for reachability analysis. This symbolic semantics enjoys the desired property that two predicate transformers are independent if they correspond to disjoint transitions in different processes. This allows us to apply standard partial order reduction techniques to the problem of checking reachability for timed systems, without disturbance from implicit synchronisation of clocks. The advantage of our approach is that we can avoid exploration of unnecessary interleavings of independent transitions. The price is that we must introduce extra machinery to perform the resynchronisation operations on local clocks. On the way, we have established a theorem about finite partitioning of the state space, analogous to the region graph for ordinary timed automata. For efficient implementation of our method, we have also presented a variant of DBM representation of symbolic states in the local time semantics. We should point out that the results of this paper can be easily extended to deal with shared variables by modifying the predicate transformer in the form ) for clock resynchronisation to the form properly for the reading and writing operations. Future work naturally include an implementation of the method, and experiments with case studies to investigate the practical significance of the approach.

## **Related Work**

Currently we have found in the literature only two other proposals for partial order reduction for real time systems: The approach by Pagani in [Pag96] for

--- end of page.page_number=123 ---

Partial Order Reductions for Timed Systems

112

timed automata (timed graphs), and the approach of Yoneda et al. in [YSSC93, YS97] for time Petri nets.

In the approach by Pagani a notion of independence between transitions is defined based on the global-time semantics of timed automata. Intuitively two transitions are independent iff we can fire them in any order and the resulting states have the same control vectors and clock assignments. When this idea is lifted to the symbolic semantics, it means that two transitions can be independent only if they can happen in the same global time interval. Thus there is a clear difference to our approach: Pagani’s notion of independence requires the comparison of clocks, while ours doesn’t.

Yoneda et al. present a partial order technique for model checking a timed LTL logic on time Petri nets [BD91]. The symbolic semantics consists of constraints on the differences on the possible firing times of enabled transitions instead of clock values. Although the authors do not give an explicit definition of independence (like our Theorem 5) their notion of independence is structural like ours, because the persistent sets, ready sets, are calculated using the structure of the net. The difference to our approach lies in the calculation of the next state in the state-space generation algorithm. Yoneda et al. store the relative firing order of enabled transitions in the clock constraints, so that a state implicitly remembers the history of the system. This leads to branching in the state space, a thing which we have avoided. A second source of branching in the state space is synchronisation. Since a state only contains information on the relative differences of firing times of transitions it is not possible to synchronise clocks.

**Acknowledgement:** We would like to thank Paul Gastin, Florence Pagani and Stavros Tripakis for their valuable comments and discussions.

## **References**

- [AD90] R. Alur and D. Dill. Automata for Modelling Real-Time Systems. In Proc. of of International Colloquium on Algorithms, Languages and Programming, volume 443 of LNCS, pages 322–335. Springer Verlag, 1990.

- [BD91] B. Berthomieu and M. Diaz. Modelling and verification of time dependent systems using time Petri nets. IEEE Transactions on Software Engineering, 17(3):259–273, 1991.

- [Bel57] R. Bellman. Dynamic Programming. Princeton University Press, 1957.

--- end of page.page_number=124 ---

Partial Order Reductions for Timed Systems

113

- [BGK 96] J. Bengtsson, D. Griffioen, K. Kristoffersen, K. G. Larsen, F. Larsson, P. Pettersson, and W. Yi. Verification of an Audio Protocol with Bus Collision Using UPPAAL. In Proc. of 9th Int. Conf. on Computer Aided Verification, volume 1102 of LNCS, pages 244–256. Springer Verlag, 1996.

- [BLL 96] J. Bengtsson, K. G. Larsen, F. Larsson, P. Pettersson, and W. Yi. UPPAAL in 1995. In Proc. of the 2nd Workshop on Tools and Algorithms for the Construction and Analysis of Systems, volume 1055 of Lecture Notes in Computer Science, pages 431–434. Springer Verlag, 1996.

- [DOTY95] C. Daws, A. Olivero, S. Tripakis, and S. Yovine. The tool KRONOS. In Proc. of Workshop on Verification and Control of Hybrid Systems III, volume 1066 of LNCS, pages 208–219. Springer Verlag, 1995.

- [Fuj90] R. M. Fujimoto. Parallel discrete event simulation. Communications of the ACM, 33(10):30–53, Oct. 1990.

- [God96] P. Godefroid. Partial-Order Methods for the Verification of Concurrent Systems: An Approach to the State-Explosion Problem, volume 1032 of LNCS. Springer Verlag, 1996.

- [GW90] P. Godefroid and P. Wolper. Using partial orders to improve automatic verification methods. In Proc. of Workshop on Computer Aided Verification, 1990.

- [HH95] T. A. Henzinger and P.-H. Ho. HyTech: The Cornell HYbrid TECHnology Tool. Proc. of Workshop on Tools and Algorithms for the Construction and Analysis of Systems, 1995. BRICS report series NS–95–2.

- [HP94] G. J. Holzmann and D. A. Peled. An improvement in formal verification. In Proc. of the 7th International Conference on Formal Description Techniques, pages 197–211, 1994.

- [LLPY97] F. Larsson, K. G. Larsen, P. Pettersson, and W. Yi. Efficient Verification of Real-Time Systems: Compact Data Structures and State-Space Reduction. In Proc. of the 18th IEEE Real-Time Systems Symposium, pages 14–24, December 1997.

- [LPY95] K. G. Larsen, P. Pettersson, and W. Yi. Compositional and Symbolic Model-Checking of Real-Time Systems. In Proc. of the 16th IEEE RealTime Systems Symposium, pages 76–87, December 1995.

- [Ove81] W. Overman. Verification of Concurrent Systems: Function and Timing. PhD thesis, UCLA, Aug. 1981.

- [Pag96] F. Pagani. Partial orders and verification of real-time systems. In Proc. of Formal Techniques in Real-Time and Fault-Tolerant Systems, volume 1135 of LNCS, pages 327–346. Springer Verlag, 1996.

- [Pel93] D. Peled. All from one, one for all, on model-checking using representatives. In Proc. of 5th Int. Conf. on Computer Aided Verification, volume 697 of LNCS, pages 409–423. Springer Verlag, 1993.

--- end of page.page_number=125 ---

Partial Order Reductions for Timed Systems

114

- [Val90] A. Valmari. Stubborn sets for reduced state space generation. In Advances in Petri Nets, volume 483 of LNCS, pages 491–515. Springer Verlag, 1990.

- [Val93] A. Valmari. On-the-fly verification with stubborn sets. In Proc. of 5th Int. Conf. on Computer Aided Verification, volume 697 of LNCS, pages 59–70, 1993.

- [YPD94] W. Yi, P. Pettersson, and M. Daniels. Automatic Verification of RealTime Communicating Systems By Constraint-Solving. In Proc. of the 7th International Conference on Formal Description Techniques, 1994.

- [YS97] T. Yoneda and H. Schlingloff. Efficient verification of parallel real-time systems. Journal of Formal Methods in System Design, 11(2):187–215, 1997.

- [YSSC93] T. Yoneda, A. Shibayama, B.-H. Schlingloff, and E. M. Clarke. Efficient verification of parallel real-time systems. In Proc. of 5th Int. Conf. on Computer Aided Verification, volume 697 of LNCS, pages 321–332. Springer Verlag, 1993.

--- end of page.page_number=126 ---

## **Paper E:**

**Automated Verification of an Audio-Control Protocol using UPPAAL**

Johan Bengtsson, W. O. David Griffioen, Kåre J. Kristoffersen, Kim G. Larsen, Fredrik Larsson, Paul Pettersson and Wang Yi.

--- end of page.page_number=127 ---

--- end of page.page_number=128 ---

117

## **Automated Verification of an Audio-Control Protocol using** UPPAAL

## Johan Bengtsson W. O. David Griffioen Kåre J. Kristoffersen Kim G. Larsen Fredrik Larsson Paul Pettersson Wang Yi

Department of Computer Systems, Uppsala University, Sweden. Email: {johanb,fredrikl,paupet,yi}@docs.uu.se. CWI, Amsterdam, The Netherlands. Email: griffoe@cwi.nl. BRICS, Aalborg University, Denmark. Email: {jelling,kgl}@cs.auc.dk.

**Abstract.** In this paper we present a case-study in which the tool UPPAAL is extended and applied to verify an Audio-Control Protocol developed by Philips. The size of the protocol studied in this paper is significantly larger than case studies, including various abstract versions of the same protocol without bus-collision handling, reported previously in the community of real-time verification. We have checked that the protocol will function correctly if the timing error of its components is bound to , and incorrectly if the error is . In addition, using UPPAAL’s ability of generating diagnostic traces, we have studied an erroneous version of the protocol actually implemented by Philips, and constructed a possible execution sequence explaining the error.

During the case-study, UPPAAL was extended with the notion of _committed locations_ . It allows for accurate modelling of atomic behaviours, and more importantly, it is utilised to guide the state-space exploration of the model checker to avoid exploring unnecessary interleavings of independent transitions. Our experimental results demonstrate considerable time and space-savings of the modified model checking algorithm. In fact, due to the huge time and memory-requirement, it was impossible to check a simple reachability property of the protocol before the introduction of committed locations, and now it takes only seconds.

## **1 Introduction**

In the past decade a number of tools for automatic verification of hybrid and real-time systems have emerged, e.g. HYTECH [HHWT97], KRONOS [Yov97], PMC [ST01], RT-Cospan [AK95] and UPPAAL [LPY97a]. These tools have by now reached a state, where they are mature enough for industrial applications.

--- end of page.page_number=129 ---

118

In this paper, we substantiate the claim by reporting on an industry-size case study where the tool UPPAAL is applied.

We analyse an audio control protocol developed by Philips for the physical layer of an interface bus connecting the various devices e.g. CD-players, amplifier etc. in audio equipments. It uses Manchester encoding to transmit bit sequences of arbitrary length between the components, whose timing errors are bound. A simplified version of the protocol is studied by Bosscher et.al. [BPV94]. It is showed that the protocol is incorrect if the timing error of the components is or greater. The proof is carried out without tool support. The first automatic analysis of the protocol is reported in [HWT95] where HYTECH is applied to check an abstract version of the protocol and automatically synthesise the upper bound on the timing error. Similar versions of the protocol have been analysed by other tools, e.g. UPPAAL [LPY97a] and KRONOS [Yov97]. However, all the proofs are based on a simplification on the protocol, introduced by Bosscher _et.al._ in 1994, that only one sender is transmitting on the bus so that no bus collisions can occur. In many applications the bus will have more than one sender, and the full version of the protocol by Philips therefore handles bus collisions. The protocol with bus collision handling was manually verified in [Gri94] without tool support. Since 1994, it has been a challenge for the verification tool developers to automate the analysis on the full version of the protocol.

The first automated proof of the protocol with bus collision handling was presented in 1996 in the conference version of this paper [BGK 96]. It was the largest case study, reported in the literature on verification of timed systems, which has been considered as a primary example in the area (see [CW96, LSW97]). The size of the protocol studied is significantly larger than various simplified versions of the same protocol studied previously in the community, e.g. the discrete part of the state space (the node-space) is times larger than in the case without bus collision handling and the number of clocks, variables and channels in the model is also increased considerably.

The major problem in applying automatic verification tools to industrial-size systems is the huge time and memory-usage needed to explore the state-space of a network (or product) of timed automata, since the verification tools must keep information not only on the control structure of the automata but also on the clock values specified by clock constraints. It is known as the state–space explosion problem. We experienced the problem right on the first attempt in checking a simple reachability property of the protocol using UPPAAL, which did not terminate in hours though it was installed on a super computer with giga-

--- end of page.page_number=130 ---

119

bytes of main memory. We observed that in addition to the size and complexity of the problem itself, one of the main causes to the explosion was the inaccurate modelling of atomic behaviours and inefficient search of the unnecessary interleavings of atomic behaviours by the tool. As a simple solution, during the case-study, UPPAAL was extended with the notion of _committed locations_ . It allows for accurate modelling of atomic behaviours, and more importantly, it is utilised in the state-space exploration of the model checker to avoid exploring unnecessary interleavings of independent transitions. Our experimental results demonstrate that the modified model-checking algorithm consume less time and space than the original algorithm. In fact, due to the huge time and memory-requirement, it was impossible to check certain properties of the protocol before the introduction of committed locations, and now it takes only seconds.

The automated analysis was originally carried out using an UPPAAL version extended with the notion of committed location installed on a super computer, a SGI ONYX machine [BGK 96]. To make a comparison, in this paper we present an application of the current version (version 3.2) of UPPAAL, also supporting committed location, installed on an ordinary Pentium II 375 MHz PC machine, to the protocol. We have checked that the protocol will function correctly if the timing error of its components is bound to , and incorrectly if the error is . In addition, using UPPAAL’s ability of generating diagnostic traces, we have studied an erroneous version of the protocol actually implemented by Philips in their audio products, and constructed a possible execution sequence explaining a known error.

The paper is organised as follows: In the next two sections we present the UPPAAL model with committed location and describe its implementation in the tool. In section 4 and 5 the Philips Audio-Control Protocol with Bus Collision is informally and formally described. The analysis of the protocol is presented in section 6 where we also compare the performance of the current UPPAAL version with the one used in [BGK 96]. Section 7 concludes the paper. Finally, formal descriptions of the protocol components are enclosed in the appendix.

## **2 Committed Locations**

The basis of the UPPAAL model for real-time systems is networks of timed automata extended with data variables [AD90, HNSY94, YPD94]. However, to meet requirements arising from various case-studies, the UPPAAL model has

--- end of page.page_number=131 ---

120


![](content_assets/paper.pdf-0132-02.png)


Figure 1: Broadcasting Communication and Committed Locations.

been extended with various new features such as urgent transitions [BLL 95] etc. The present case-study indicates that we need to further extend the UPPAAL model with _committed locations_ to model atomic behaviours such as multiway synchronisations and atomic broadcasting in real-time systems. Our experiences with UPPAAL show that the notion of committed locations introduced in UPPAAL is not only useful in modelling but also yields significant improvements in performance.

We assume that a real-time system consists of a fixed number of sequential processes communicating with each other via channels. We further assume that each communication synchronises two processes as in CCS [Mil89]. Broadcasting communication can be implemented in such systems by repeatedly sending the same message to all the receivers. To ensure atomicity of such “broadcast” sequences we mark the intermediate locations of the sender, which are to be executed immediately, as so-called _committed locations_ .

## **2.1 An Example**

To introduce the notion of committed locations in timed automata, consider the scenario shown in Figure 1. A sender S is to broadcast a message m to two receivers R and R . As this requires synchronisation between _three_ processes this can not directly be expressed in the UPPAAL model, where synchronisation is between two processes with complementary actions. As an initial attempt we may model the broadcast as a sequence of two two-process synchronisations,

--- end of page.page_number=132 ---

121

where first S synchronises with R on m and then with R on m . However, this is not an accurate model as the intended atomicity of the broadcast is not preserved (i.e. other processes may interfere during the broadcast sequence). To ensure atomicity, we mark the intermediate location S of the sender S as a _committed location_ (indicated by the c:-prefix). The atomicity of the action sequence m !m ! is now achieved by insisting that a committed sequence must be left immediately! This behaviour is similar to what has been called “urgent transitions” [HHWT95, DY95, BLL 95], which insists that the next transition taken must be an action (and not a delay), but the essential difference is that no other actions should be performed in between such an atomic sequence. The precise semantics of committed locations will be formalised in the transition rules for networks of timed automata with data variables in Section 2.3.

## **2.2 Syntax**

We assume a finite set of clock variables ranged over by and a finite set of data variables ranged over by . We use to stand for the set of _clock constraints_ that are the conjunctive formulas of simple constraints in the form of or , where and is a natural number. Similarly, we use to stand for the set of _non-clock constraints_ that are conjunctive formulas of or , where and is an integer number. We use ranged over by to denote the set of formulas that are conjunctions of clock constraints and a non-clock constraints. The elements of are called _constraints_ or _guards_ .

To manipulate clock and data variables, we use reset-sets which are finite sets of reset-operations. A reset-operation on a clock variable should be in the form where is a natural number and a reset-operation on an data variable should be in the form: where are integers. A reset-set is a _proper_ reset-set when the variables are assigned a value at most once, we use to denote the set of all proper reset-sets.

We assume that processes synchronise with each other via complementary actions. Let be a set of action names with a subset of urgent actions on which processes should synchronise whenever possible. We use ct to denote the set of actions that processes can perform to synchronise with each other, where is a distinct symbol representing internal actions. We use name to denote the action name of , defined by name name .

--- end of page.page_number=133 ---

122

An automaton over actions ct, clock variables and data variables is a tuple where is a finite set of locations (control-locations) with a subset being the set of committed locations, is the initial location, ct corresponds to the set of edges, and is the invariant assignment function. To model urgency, we require that the guard of an edge with an urgent action is a non-clock constraint, i.e. if name and then .

In the case, we shall write which represents a transition from the location to the location with guard , action to be performed, and a sequence of reset-operations to update the variables. Furthermore, we shall write whenever .

To model networks of processes, we introduce a CCS-like parallel composition operator for automata. Assume that are automata. We use to denote their parallel composition. The intuitive meaning of is similar to the CCS parallel composition of with _all_ actions being restricted, that is, ct. Thus only synchronisation between the components is possible. We call a _network of automata_ . We simply view as a vector and use to denote its th component.

## **2.3 Semantics**

Informally, a process modelled by an automaton starts at location with all its variables initialised to . The values of the clocks may increase synchronously with time at location as long as the invariant condition is satisfied. At any time, the process can change location by following an edge provided the current values of the variables satisfy the enabling condition . With this transition, the variables are updated by .

To formalise the semantics we shall use variable assignments. A _variable assignment_ is a mapping which maps clock variables to the non-negative reals and data variables to integers. For a variable assignment and a delay , denotes the variable assignment such that for a clock variable and for any data variable . This definition of reflects that all clocks proceed at the same speed and that data variables are time-insensitive.

For a reset-set (a proper set of reset-operations), we use to denote the variable assignment with Value whenever and otherwise, where Value denotes the value of in . Given

--- end of page.page_number=134 ---

123

a constraint and a variable assignment , is a boolean value describing whether is satisfied by or not.

A _control vector_ of a network is a vector of locations where is a location of . We write to denote the vector where the th element of is replaced by . Furthermore, we shall write whenever for some .

A _state_ of a network is a configuration where is a control vector of and is a variable assignment. The initial state of is where is the initial control vector whose elements are the initial locations of ’s and is the initial variable assignment that maps all variables to .

The _semantics of a network_ of automata is given in terms of a transition system with the set of states being the configurations. The transition relation is defined by the following three rules, which are standard except that each rule has been augmented with conditions handling control-vectors with committed locations:


![](content_assets/paper.pdf-0135-06.png)


- if and for some , , , and for

- all if then .


![](content_assets/paper.pdf-0135-08.png)



![](content_assets/paper.pdf-0135-09.png)



![](content_assets/paper.pdf-0135-10.png)


- if , , ,

- , and , for some , , , , , , and for all if

- then or .


![](content_assets/paper.pdf-0135-12.png)


- if , , and no ,

- such that , , , , , and .


![](content_assets/paper.pdf-0135-14.png)



![](content_assets/paper.pdf-0135-15.png)



![](content_assets/paper.pdf-0135-16.png)



![](content_assets/paper.pdf-0135-17.png)



![](content_assets/paper.pdf-0135-18.png)


where


![](content_assets/paper.pdf-0135-20.png)



![](content_assets/paper.pdf-0135-21.png)



![](content_assets/paper.pdf-0135-22.png)


.

Intuitively, the first rule describes a local internal action transition in a component, and possibly the resetting of variables. An internal transition can occur if the current variable assignment satisfies the transition guard and if the controllocation of any component is committed, only components in committed locations may take local transitions. Thus, only internal transitions of components in committed location may interrupt other components operating in committed locations.

The second rule describes synchronisation transitions that synchronise two components. If the control-location of any of the components is committed it is required that at least one of the synchronising components starts in a committed location. This requirement prevents transitions starting in non-committed

--- end of page.page_number=135 ---

124

locations from interfering with atomic (i.e. committed) transition sequences. However, two independent committed sequences may interfere with each other.

The third rule describes delay transitions, i.e. when all clocks increase synchronously with time. Delay transitions are permitted only while the location invariants of all components are satisfied. Delays are not permitted if the controllocation of a component in the network is committed, or if an urgent transition (i.e. a synchronisation transition with urgent action) is possible. Note that the guards on urgent transitions are non-clock constraints whose truth-values are not affected by delays.

Finally, we note that the three rules give a semantics where transition sequences marked as committed are _instantaneous_ in the sense that they happen without duration, and without interference from components operating in non-committed locations.

## **3 Committed Locations in** UPPAAL

In this section we present a modified version of the model-checking algorithm of UPPAAL for networks of automata with committed locations.

## **3.1 The Model-Checking Algorithm**

The model-checking algorithm performs reachability analysis to check for invariance properties , and reachability properties , with respect to a local property of the control locations and the values of the clock and data variables[1] . It combines symbolic techniques with on-the-fly generation of the state-space in order to avoid explicit construction of the product automaton and the immediately caused memory problems. The algorithm is based on a partitioning of the (otherwise infinite) state-space into finitely many symbolic states of the form , where is a constraint system (i.e. a conjunction of clock constraints and non-clock constraints). It checks if a any part of a symbolic state (i.e. a state with ) is reachable from the initial symbolic state , where expresses that all clock and data variables are initialised to [YPD94]. Throughout the rest of this paper we shall simply call a state instead of symbolic state.

> 1 From version 3.2 released in 2001, the model-checking algorithm in UPPAAL also supports liveness properties of the kind and .

--- end of page.page_number=136 ---

125

The algorithm essentially performs a forwards search of the state-space. The search is guided and pruned by two buffers: WAITING, holding states waiting to be explored and PASSED holding states already explored. Initially, PASSED is empty and WAITING holds the single state . The algorithm then repeats the following steps:

S1. Pick a state from the WAITING buffer.

- S2. If and return the answer _yes_ .

- S3. a. If and , for some in the PASSED buffer, drop and go to step S1.

   - b. Otherwise, save in the PASSED buffer.

- S4. Find all successor states reachable from in one step and store them in the WAITING buffer.

- S5. If the WAITING buffer is not empty then go to step S1, otherwise return the answer _no_ .

We will not treat the algorithm in detail here, but refer the reader to [YPD94, BL96].

Note that in step S3.b all explored states are stored in the PASSED buffer to ensure termination of the algorithm. In many cases, it will store the whole statespace of the analysed system which grows exponentially both in the number clocks and components [YPD94]. The algorithm is therefore bound to run into space problems for large systems. The key question is how to reduce the growth of the PASSED buffer.

When committed locations are used to model atomic behaviours there are two potential possibilities to reduce the size of the PASSED buffer. First, as atomic sequences in general restrict the amount of interleaving that is allowed in a system [Hol91], the state-space of the system is reduced, and consequently also the number of states stored in the PASSED buffer. Secondly, as a sequence of committed locations semantically is instantaneous and non-interleaved with other components, it suffices to save only the (non-committed) control-location at the beginning of the sequence in the PASSED buffer to ensure termination. Hence, our proposed solution is simply _not_ to save states in the PASSED buffer which involve _committed_ locations. We modify step S3 of the algorithm in the following way:

--- end of page.page_number=137 ---

126


![](content_assets/paper.pdf-0138-02.png)


Figure 2: Broadcasting Using Committed Locations.

- S3 . a. If go directly to step S4.

   - b. If and , for some in the PASSED buffer, drop and go to step S1.

   - c. If neither of the above steps are applicable, save in the PASSED buffer.

So, for a given state , if is committed the algorithm proceeds directly from step S3 .a to step S4, thereby omitting the time-consuming step S3 .b and the space-consuming step S3 .c. Clearly, this will reduce the growth of the PASSED buffer and the total amount of time spent on step S3 . In the following step S4 more reductions are made as interleavings are not allowed when is committed. In fact, the next transition must be an action transition and it must involve a which is committed in (according to the transition rules in the previous section). This reduces the time spent on generating successor states of in S4 as well as the total number of states in the system. Finally, we note that reducing the PASSED buffer size also yields potential time-savings in step S3 .b when is _not_ committed as it involves a search through the PASSED buffer.

It should be noticed that the algorithm presented in this section is not guaranteed to terminate if the notion of committed locations is used in an unintended way[2] . For the modified algorithm to terminate, it is assumed in the that committed locations are used to model atomic behaviours. In particular this means that any sequence of committed control-locations must be of finite length.

> 2In the current implementation of UPPAAL, the algorithm uses a technique presented in [LLPY97] to identify and store at least one so-called _covering state_ in each _dynamic loop_ to guarantee termination for all input models.

--- end of page.page_number=138 ---

127


![](content_assets/paper.pdf-0139-02.png)


Figure 3: Time and Space Consumption.

## **3.2 Space and Time Performance Improvements**

To investigate the practical benefits from the usage of committed locations and its implementation in UPPAAL we perform an experiment with a parameterisable scenario, where a sender S wants to broadcast a message to receivers R R . The sender S simply performs a!-transitions and then terminates, whereas the receivers are all willing to perform a single a?-transition hereby synchronising with the sender. The data variable k ensures that the th receiver participates in the th handshake. Additionally, there are auxiliary automata D D simply oscillating between two states. Consider Figure 2, where the control node S is committed (indicated by the c:-prefix).

We may now use UPPAAL to verify that the sender succeeds in broadcasting the message, i.e. it forces all the receivers to terminate. More precisely we verify that SYS S R R D D satisfies the formula at(S,S ) at(R ,R ) , where we assume that the proposition at( , ) is implicitly assigned to each location of the automaton , meaning that the component is operating in location . We perform two verifications, one with S declared as committed, and one with S being non-committed but with a location invariant , where x is a clock which is reset on the transition from S1 to S2, preventing the automaton from delaying in location S . The result is shown in Figure 3. In both test sequences the number of disturbing automata was fixed to eight. Time is measured in seconds and space is measured in pages (4KB). The general observation is that use of committed locations in broadcasting saves time as well as space. The most important observation is

--- end of page.page_number=139 ---

128

that in the committed scenario the space consumption behaves as a constant function in the number of receivers.

## **4 The Audio Control Protocol with Bus Collision**

In this section an informal introduction to the audio protocol with bus collision is given. The audio control protocol is a bus protocol, all messages are received by all components on the bus. If a component receives a message not addressed to it, the message is just ignored. Philips allows up to 10 components.

Messages are transmitted using Manchester encoding. Time is divided into bitslots of equal length, a bit “1” is transmitted by an up-going edge halfway a bit-slot, a bit “0” by a down-going edge halfway a bit-slot. If the same bit is transmitted twice in a row the voltage must of course change at the end of the first bit-slot. Note that only a single wire is used to connect the components, no extra clock wire is needed. This is one of the properties that makes it a useful protocol.

The protocol has to cope with some problems: The sender and the receiver must agree on the beginning of the first bit-slot, the length of the message is not known in advance by the receiver, the down-going edges are not detected by the receiver. To resolve these problems the following is required: Messages must start with a bit “1” and messages must end with a down-going edge. This ensures that the voltage on the wire is low between messages. Furthermore the senders must respect a so-called “radio silence” between the end of a message and the beginning of the next one. The radio silence marks the end of a message and the receiver knows that the next up-going edge is the first edge of a new message. It is almost possible, and actually mandated in the Philips documentation, to decode a Manchester encoded message by only looking to the up-going edges (problem ) only the last zero bit of a message can not be detected (consider messages “10” and “1”). To resolve this, it is required that all messages are of odd length.

It is possible that two or more components start transmitting at the same time. The behaviour of the electric circuit is such that the voltage on the wire will be high as long as one of the senders pulls it high. In other words: The wire implements the or-function. This makes it possible for a sender to notice that someone else is also transmitting. If the wire is high while it is transmitting a low, a sender can detect a bus collision. This collision detection happens at certain points in time: Just before each up-going transition, and at one and three

--- end of page.page_number=140 ---

129


![](content_assets/paper.pdf-0141-02.png)



![](content_assets/paper.pdf-0141-03.png)



![](content_assets/paper.pdf-0141-04.png)


Figure 4: An Example.

quarters of a bit-slot after a down going edge (if it is still transmitting a low). When a sender detects a collision it will stop transmitting and will try to retransmit its message later.

If two messages are transmitted at the same time and one is a prefix of the other, the receiver will not notice the prefix message. To ensure collision detection it is not allowed that a message is a prefix of another message in transit. In the Philips environment this restriction is met by embedding the source address in each message (and assigning each component a unique source address).

In Figure 4 an example is depicted. Assume two senders, named A and B, that start transmitting at exactly the same time. Because two lines on top of each other are hard to distinguish from one line, in the picture they are shifted slightly. The sender A (depicted with thick lines) starts transmitting “11...” and sender B (depicted with thin lines) “101...”. At the end of the first bit-slot sender A changes from high to low voltage, to prepare for the next up-going edge. But one quarter after this down it detects a collision and stops transmitting. Sender B did not notice the other sender and continues transmitting. Note that the receiver will decode the message of the sender B correctly.

The protocol has to cope with one more thing: timing uncertainty. Because the protocol is implemented on a processor that also has to execute a number of other time critical tasks, a quite large timing uncertainty is allowed. A bitslot is 888 microseconds, so the ideal time between two edges is 888 or 444 microseconds. On the generation of edges a timing uncertainty of 5% is allowed. That is, between 844 and 932 for one bit-slot and between 422 and 466 for half a bit-slot. The collision detection just before an up-going edge and the actual generation of the same up-going edge should be separated by at most 20 microseconds (according to the protocol specification). The timing uncertainty on the collision detection appearing at the first and third quarters after a downgoing edge is 22 microseconds. Also the receiver has a timing uncertainty of 5%. To complete the timing information, the distance between the end of one message and the beginning of the next must be at least 8000 microseconds (8 milliseconds).

--- end of page.page_number=141 ---

130


![](content_assets/paper.pdf-0142-02.png)


Figure 5: Philips Audio-Control Protocol with Bus Collision.

## **5 A Formal Model of the Protocol**

To analyse the behaviour of the protocol we model the system as a network of seven timed automata. The network consists of two parts: a _core part_ and a _testing environment_ . The core part models the components of the protocol to be implemented: two senders, a wire and a receiver. The testing environment, consisting of two message generators (one for each sender) and an output checker, is used to model assumptions about the environment of the protocol and for testing the behaviour of the core part. Figure 5 shows a flow-graph of the network where nodes represent timed automata and edges represent synchronisation channels or shared variables, the latter enclosed within parentheses.

The general idea of the model is as follows. The two automata MessageA and MessageB are designed to non-deterministically generate possible valid messages for the both senders (as described in section 4), in addition MessageA informs the Check-automaton on the bits it generated for SenderA. The senders transmit the messages via the wire to the receiver. We have chosen to model the wire as an automaton to separate its behaviour from the two senders and the receiver. The receiver communicates the bits it decoded to the checker. Thus the Check automaton is able to compare the bits generated by MessageA and the bits received by Receiver. If this matches the protocol is correct.

The senders A and B are, modulo renaming (all A’s in identifiers to B’s), exactly the same. Because of the symmetry, it is enough to check that the messages transmitted by sender A are received correctly. If a scenario exits in which a message of sender B is received incorrectly, the same scenario (modulo renaming) exists for sender A. We will proceed with a short description of each

--- end of page.page_number=142 ---

131

automaton. The definition of these uses a number of constants that are declared in Table 1 in Appendix 8.

## **The Senders**

SenderA is depicted in Figure 10. It takes input actions Ahead0?, Ahead1? and Aempty?. The output actions UP! and DOWN! will be the Manchester encoding of the message. The clock Ax is used to measure the time between UP! and DOWN! actions. The idea behind the model (taken from [DY95]) is that the sender changes location each half of a bit-slot. The locations HS (wire is High in Second half of the bit-slot) and HF (High in First half of the bit-slot) refer to this idea. Extra locations are needed because of the collision detection.

The clock Ad is used to measure the time elapsed between the detection just before UP! action and the corresponding UP! action. The system is in the locations ar_Qfirst and ar_Qlast when the next thing to do is the collision test at one or three quarters of a bit-slot. When Volt is greater than zero, at that moment, the sender detects a collision, stops transmitting and returns to the idle location. The clock w is used to ensure the radio silence between messages. This variable is checked on the transition from idle to ar_first_up.

## **The Wire**

This small automaton keeps track of the voltage on the wire and generates VUP! actions when appropriate, that is when a UP? action is received when the voltage is low. The automaton is shown in Figure 9.

## **The Receiver**

Receiver, shown in Figure 8, decodes the bit sequence using the up-going (modelled as VUP?) changes of the wire. Decoded bits are signalled to the environment using output actions Add0!, Add1! and OUT! (where OUT! is used for signalling the end of a decoded message). The decoding algorithm of the receiver is a direct translation of the algorithm in the Philips documentation of the protocol. In the automaton each VUP? transition is followed by a transition modelling the decoding. This decoding happens at once, therefore the intermediate locations are modelled as committed locations. The automaton has two important locations, L1 and L0. When the last received bit is a bit “1” the receiver is in location L1, after receiving a bit “0” it will be in location L0. The error location is entered when a VUP? is received much too early. In the complete model the error location is not reachable, see Section 6. The receiver

--- end of page.page_number=143 ---

132

keeps track of the parity of the received message using the integer variable odd. When the last received bit is a bit “1” and the message is even, a bit “0” is added to make the complete message of odd length.

## **The Message Generators**

The message generators MessageA and MessageB, shown in Figure 11, generate valid messages (i.e. any message for which the protocol should behave correctly according to the specification) for sender A and B. In addition, the messages generated for sender A are communicated to the checker. The start of a message is signalled to the checker by AINc!, bits by expect0! and expect1!. When a collision is detected by sender A this is communicated to MessageA via Acoll?. The message generator will communicate this on his turn to the check automaton via CAcoll!.

Generating messages of odd length is quite simple. The only problem is that it is not allowed that a message for one sender is a prefix of the message for the other sender. To be more precise: If only one sender is transmitting there is no prefix restriction. Only when the two senders start transmitting at the same time, it is not allowed that one sender transmits a prefix of the message transmitted by the other. As mentioned before the reason for this restriction is that the prefix message is not received by the receiver and it is possible that the senders do not notice the collision. In other words: the prefix message can be lost. To ensure that the two generated bit-streams differ on at least on position, the generator always compare the last generated bit-values stored in the variables lb and Blb on the edge from locations sending0 or sending1 to location sending. If the bits differ, the variable ok is set to 1, which is a requirement for the message generation to end normally (on the transition from sending to idle in the two automata).

## **The Checker**

This automaton is shown in Figure 7. It keeps track of the bits “in transit”, i.e. the bits that are generated by the message generators but not yet decoded by the receiver. These bits are encoded using the two variables l, which stores the length of the bit-stream, and r that stores the actual bit-stream in transit. Whenever a bit is decoded or the end of the message is detected not conform the generated message the checker enters location error. Furthermore, when sender A detects a collision the checker returns to its initial location.

--- end of page.page_number=144 ---

133

## **6** UPPAAL

In this section we present the results of analysing the Philips audio-control protocol formally described in the previous section. We will use to denote the (implicit) proposition at( ) introduced in Section 3.2. Also, note that invariance properties in UPPAAL are on the form , where is a local property.

## **Correctness Criteria**

The main correctness criterion of the protocol is to ensure that the bit sequence received by the Receiver matches the bit sequence sent by SenderA. Moreover, the _entire_ bit sequence should be received by Receiver (and communicated to Check). From the description of the Check-automaton (see the previous section) it follows that this behaviour is ensured if Check is always operating in location start or normal:


![](content_assets/paper.pdf-0145-06.png)



![](content_assets/paper.pdf-0145-07.png)



![](content_assets/paper.pdf-0145-08.png)


When the Receiver-automaton observes changes of the wire too early it changes control to location error. If the rest of the components behave normally this should not happen. Therefore, the Receiver-automaton is required to never reach the location error:


![](content_assets/paper.pdf-0145-10.png)



![](content_assets/paper.pdf-0145-11.png)


## Receiver error (2)

## **Incorrectness**

Unfortunately the protocol described in this paper is not the protocol that Philips has implemented. The original sender checked less often for a bus collision. The “just before the up going edge” collision detection was only performed before the first up. In the UPPAAL model this corresponds to deleting outgoing transitions of ar_Qlast_ok and using the outgoing transitions of ar_up_ok instead. This incorrect version is shown in Figure 12. In general the problem is that if both senders are transmitting and one is slow and the other fast, the distance can cumulate to a high value that can confuse the receiver. UPPAAL generated a counter-example trace to Property 1. The trace is depicted in Figure 6. The scenario is as follows: Sender A (depicted with thick lines) tries to transmit “111...” and sender B (depicted with thin lines) “1100...”. The sender A is fast and the other slow. This causes the distance between the second UP’s to be very big (77 microseconds). In the third bit-slot the sender A detects the collision. The result of all this is that the time elapsed between the VUP actions is 6.65Q instead of

--- end of page.page_number=145 ---

134


![](content_assets/paper.pdf-0146-02.png)


Figure 6: Error execution of the incorrect protocol.

the ideal 6Q. Because of the timing uncertainty in the receiver this can be interpreted as 7Q ( ), and 7Q is just enough to decode “01” instead of the transmitted “0”. Thus, it is possible that the sent and received message differ with this version of the protocol.

In the correct version this scenario is impossible, because if collision detection happens before _every_ UP action, the distance between the UP’s in the second bit-slot can not be that high (at most 20 microseconds).

It is not likely that these kind of errors happen in the actual implementation. First, it is not likely that two senders do start at sufficiently close time-points. Secondly, the timing uncertainty is at most 2% instead of 5%, and the “average” timing uncertainty is even less. For more details, see [Gri94].

Although this problem was known by Philips it is interesting to see how powerful the diagnostic traces can be. It enables us not only to find mistakes in the _model_ of a protocol, but also to find design mistakes in real-life protocols.

##

UPPAAL successfully verifies the correctness properties 1 and 2 for an error tolerance of 5% on the timing. Recall that SenderA and SenderB are, modulo renaming, exactly the same, implying that the verified properties for SenderA also applies to the symmetric case for SenderB. The verification of Property 1 and 2 was performed in 0.5 sec using 2.5 MB of memory.

The analysis of the incorrect version of the protocol with less collision detection (discussed above) uses UPPAAL’s ability to generate diagnostic traces whenever an invariant property is not satisfied by the system. The trace, consisting of 46 transitions, was generated in 0.4 sec using 2.5 MB of memory. Also, verification of Property 1 for the protocol with full collision detection and an error tolerance

--- end of page.page_number=146 ---

135

of 6% on all the timing produces an error trace as well. The scenario is similar to the one found by Bosscher et.al. in [BPV94] for the one sender protocol.

The properties were verified using UPPAAL version 3.2 [LPY97a, BLL 98, ABB 01] that implements the verification algorithm handling committed locations described in Section 3. It was installed on a Pentium II 375 MHz PC running Debian Linux 2.2. In the conference version of this paper [BGK 96] we reported that the same protocol was verified using UPPAAL version 0.96[3] installed on a SGI ONYX machine. The verification of the two correctness properties then consumed 7.5 hrs using 527.4 MB and 1.32 hrs using 227.9 MB, whereas a diagnostic trace for the incorrect version was generated in 13.0 min using 290.4 MB of memory. Hence, both the time- and space-consumption of the verifier for this particular model have been reduced with over 99%. These improvements of the UPPAAL verifier are due to a number of developments in the last years that will not be discussed further here. It should also be noticed that the older version uses backwards analysis whereas the newer performs forwards analysis. For more information he developments of UPPAAL we refer the reader to [LPY97b, BLL 98, ABB 01].

## **7 Conclusions**

In this paper we have presented a case-study where the verification tool UPPAAL is used to verify an industrial audio-control protocol with bus-collision handling by Philips. The protocol has received a lot of attention in the formal methods research community (see e.g. [BPV94, HWT95, CW96]) and simplified versions of the protocol without the handling of bus collisions have previously been analysed by several research teams, with and without support from automatic tools.

As verification results we have shown that the protocol behaves correctly if the error on all timing is bound to 5%, and incorrectly if the error is 6%. Furthermore, using UPPAAL’s ability to generate diagnostic traces we have been able to study error scenarios in an incorrect version of the protocol actually implemented by Philips.

In this paper we have also introduced the notion of so-called committed locations which allows for more accurate modelling of atomic behaviours. More importantly, it is also utilised to guide the state-space exploration of the model

3 The two UPPAAL versions 0.96 and 2.17 are dated Nov 1995 and March 1998 respectively.

--- end of page.page_number=147 ---

136

checker to avoid exploring unnecessary interleavings of independent transitions. Our experimental results demonstrate considerable time and space-savings of the modified model checking algorithm. In fact, due to the huge time and memory-requirement, it was impossible to check certain properties of the protocol before the introduction of committed locations, and now it takes only seconds.

## **References**

- [ABB 01] Tobias Amnell, Gerd Behrmann, Johan Bengtsson, Pedro R. D’Argenio, Alexandre David, Ansgar Fehnker, Thomas Hune, Bertrand Jeannet, Kim G. Larsen, M. Oliver Möller, Paul Pettersson, Carsten Weise, and Wang Yi. UPPAAL - Now, Next, and Future. In F. Cassez, C. Jard, B. Rozoy, and M. Ryan, editors, _Modelling and Verification of Parallel Processes_ , number 2067 in Lecture Notes in Computer Science, pages 100–125. Springer–Verlag, 2001.

- [AD90] Rajeev Alur and David Dill. Automata for Modelling Real-Time Systems. In _Proc. of Int. Colloquium on Algorithms, Languages and Programming_ , number 443 in Lecture Notes in Computer Science, pages 322–335, July 1990.

- [AK95] Rajeev Alur and Robert P. Kurshan. Timing Analysis in COSPAN. In Rajeev Alur, Thomas A. Henzinger, and Eduardo D. Sontag, editors, _Proc. of Workshop on Verification and Control of Hybrid Systems III_ , number 1066 in Lecture Notes in Computer Science, pages 220–231. Springer– Verlag, October 1995.

- [BGK 96] Johan Bengtsson, W.O. David Griffioen, Kåre J. Kristoffersen, Kim G. Larsen, Fredrik Larsson, Paul Pettersson, and Wang Yi. Verification of an Audio Protocol with Bus Collision Using UPPAAL. In Rajeev Alur and Thomas A. Henzinger, editors, _Proc. of the 8th Int. Conf. on Computer Aided Verification_ , number 1102 in Lecture Notes in Computer Science, pages 244–256. Springer–Verlag, July 1996.

- [BL96] Johan Bengtsson and Fredrik Larsson. UPPAAL a Tool for Automatic Verification of Real-time Systems. Master’s thesis, Uppsala University, 1996. Available as http://www.docs.uu.se/docs/rtmv/bl-report.pdf.

- [BLL 95] Johan Bengtsson, Kim G. Larsen, Fredrik Larsson, Paul Pettersson, and Wang Yi. UPPAAL — a Tool Suite for Automatic Verification of Real– Time Systems. In _Proc. of Workshop on Verification and Control of Hybrid Systems III_ , number 1066 in Lecture Notes in Computer Science, pages 232–243. Springer–Verlag, October 1995.

--- end of page.page_number=148 ---

137

- [BLL 98] Johan Bengtsson, Kim G. Larsen, Fredrik Larsson, Paul Pettersson, Wang Yi, and Carsten Weise. New Generation of UPPAAL. In _Int. Workshop on Software Tools for Technology Transfer_ , June 1998.

- [BPV94] D. Bosscher, I. Polak, and F. Vaandrager. Verification of an Audio-Control Protocol. In _Proc. of Formal Techniques in Real-Time and Fault-Tolerant Systems_ , number 863 in Lecture Notes in Computer Science, 1994.

- [CW96] Edmund M. Clarke and Jeanette M. Wing. Formal Methods: State of the Art and Future Directions. _ACM Computing Surveys_ , 28(4):626–643, December 1996.

- [DY95] C. Daws and S. Yovine. Two examples of verification of multirate timed automata with KRONOS. In _Proc. of the 16_ th _IEEE Real-Time Systems Symposium_ , pages 66–75. IEEE Computer Society Press, December 1995.

- [Gri94] W.O. David Griffioen. Analysis of an Audio Control Protocol with Bus Collision. Master’s thesis, University of Amsterdam, Programming Research Group, 1994.

- [HHWT95] Thomas A. Henzinger, Pei-Hsin Ho, and Howard Wong-Toi. HYTECH: The Next Generation. In _Proc. of the 16_ th _IEEE Real-Time Systems Symposium_ , pages 56–65. IEEE Computer Society Press, December 1995.

- [HHWT97] Thomas A. Henzinger, Pei-Hsin Ho, and Howard Wong-Toi. HYTECH: A Model Checker for Hybrid Systems. _Int. Journal on Software Tools for Technology Transfer_ , 1(1–2):134–152, October 1997.

- [HNSY94] Thomas. A. Henzinger, Xavier Nicollin, Joseph Sifakis, and Sergio Yovine. Symbolic Model Checking for Real-Time Systems. _Information and Computation_ , 111(2):193–244, 1994.

- [Hol91] Gerard Holzmann. _The Design and Validation of Computer Protocols_ . Prentice Hall, 1991.

- [HWT95] Pei-Hsin Ho and Howard Wong-Toi. Automated Analysis of an Audio Control Protocol. In _Proc. of the 7th Int. Conf. on Computer Aided Verification_ , number 939 in Lecture Notes in Computer Science. Springer– Verlag, 1995.

- [LLPY97] Fredrik Larsson, Kim G. Larsen, Paul Pettersson, and Wang Yi. Efficient Verification of Real-Time Systems: Compact Data Structures and StateSpace Reduction. In _Proc. of the_ 18th IEEE Real-Time Systems Symposium, pages 14–24. IEEE Computer Society Press, December 1997.

- [LPY97a] Kim G. Larsen, Paul Pettersson, and Wang Yi. UPPAAL in a Nutshell. _Int. Journal on Software Tools for Technology Transfer_ , 1(1–2):134–152, October 1997.

--- end of page.page_number=149 ---

138

- [LPY97b] Kim G. Larsen, Paul Pettersson, and Wang Yi. UPPAAL: Status and Developments. In Orna Grumberg, editor, _Proc. of the 9th Int. Conf. on Computer Aided Verification_ , number 1254 in Lecture Notes in Computer Science, pages 456–459. Springer–Verlag, June 1997.

- [LSW97] Kim G. Larsen, Bernard Steffen, and Carsten Weise. Continuous modeling of real-time and hybrid systems: from concepts to tools. _Int. Journal on Software Tools for Technology Transfer_ , 1(1–2):64–85, December 1997.

- [Mil89] R. Milner. _Communication and Concurrency_ . Prentice Hall, Englewood Cliffs, 1989.

- [ST01] R. F. Lutje Spelberg and W. J. Toetenel. Parametric real-time model checking using splitting trees. _Nordic Journal_ , 8(1):88–120, 2001.

- [Yov97] Sergio Yovine. A Verification Tool for Real Time Systems. _Int. Journal on Software Tools for Technology Transfer_ , 1(1–2):134–152, October 1997.

- [YPD94] Wang Yi, Paul Pettersson, and Mats Daniels. Automatic Verification of Real-Time Communicating Systems By Constraint-Solving. In Dieter Hogrefe and Stefan Leue, editors, _Proc. of the 7_ th _Int. Conf. on Formal Description Techniques_ , pages 223–238. North–Holland, 1994.

--- end of page.page_number=150 ---

139

## **8 Appendix**

|The constants used in the|The constants used in the|formulas|
|---|---|---|
|q|2220|One quarter of a bit-slot: 222 micro sec|
|d|200|Detection ’just before’ the UP:|
|||20 micro sec|
|g|220|’Around’ 25% and 75% of the bit-slot:|
|||22 micro sec|
|w|80000|The radio silence: 8 milli sec|
|t|0.05|The timing uncertainty: 5%|
|The constants in the automata|||
|W|w|80000|
|D|d|200|
|A1min|q-g|2000|
|A1max|q+g|2440|
|A2min|3*q-g|6440|
|A2max|3*q+g|6880|
|Q2|2*q|4440|
|Q2minD|2*q*(1-t)-d|4018|
|Q2min|2*q*(1-t)|4218|
|Q2max|2*q*(1+t)|4662|
|Q3min|3*q*(1-t)|6327|
|Q3max|3*q*(1+t)|6993|
|Q5min|5*q*(1-t)|10545|
|Q5max|5*q*(1+t)|11655|
|Q7min|7*q*(1-t)|14763|
|Q7max|7*q*(1+t)|16317|
|Q9min|9*q*(1-t)|18981|
|Q9max|9*q*(1+t)|20979|



Table 1: Declaration of Constants.

--- end of page.page_number=151 ---

140


![](content_assets/paper.pdf-0152-02.png)


Figure 7: The Check Automaton.


![](content_assets/paper.pdf-0152-04.png)


Figure 8: The Receiver Automaton.

--- end of page.page_number=152 ---

141


![](content_assets/paper.pdf-0153-02.png)


Figure 9: The Wire Automaton.


![](content_assets/paper.pdf-0153-04.png)


Figure 10: The SenderA Automaton.

--- end of page.page_number=153 ---

142


![](content_assets/paper.pdf-0154-02.png)


Figure 11: The Message Automata.

--- end of page.page_number=154 ---

143


![](content_assets/paper.pdf-0155-02.png)


Figure 12: The Incorrect SenderA Automaton.

--- end of page.page_number=155 ---
