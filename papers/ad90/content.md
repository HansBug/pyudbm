# Automata for Modeling Real-Time Systems

Rajeev Alur<sup>1</sup>  
David Dill<sup>2</sup>  
Department of Computer Science, Stanford University, U.S.A.

> Note: the local `paper.pdf` in this directory is only a two-page Springer preview, not the full chapter. The Markdown below therefore transcribes only the material available in that preview.

## Abstract

To model the behavior of finite-state asynchronous real-time systems, we propose the notion of timed Buchi automata (TBA). TBAs are Buchi automata coupled with a mechanism to express constant bounds on the timing delays between system events. These automata accept languages of timed traces, traces in which each event has an associated real-valued time of occurrence.

We show that the class of languages accepted by TBAs is closed under the operations of union, intersection, and projection, and that the trace language obtained by projecting the language accepted by a TBA is $\omega$-regular. It turns out that TBAs are not closed under complement, and it is undecidable whether the language of one automaton is a subset of the language of another. This result is an obstruction to automatic verification. However, we show that a significant proper subclass, represented by deterministic timed Muller automata (DTMA), is closed under all Boolean operations. Consequently, a system modeled by a TBA can be automatically verified with respect to a specification given as a DTMA.

<sup>1</sup> Supported by the NSF grant CCR-8812595, the DARPA contract N00039-84-C-0211, and the USAF Office of Scientific Research under contracts 88-0281 and 90-0057.

<sup>2</sup> Supported by the NSF grant MIP-8858807.

## 1 Introduction

Modal logics and $\omega$-automata for qualitative temporal reasoning about concurrent systems have been studied in great detail (selected references: [Ch74, WVS83, CES86, Pn86, Di88, CDK89]). These formalisms abstract away from time, retaining only the sequencing of events in a system. In the automata-theoretic approach, a system is modeled as a finite-state nondeterministic automaton on infinite strings, for example a Buchi automaton; the language accepted by the automaton corresponds to the set of possible behaviors of the system. The operations useful for describing complex systems can then be viewed as language-theoretic operations. For example, parallel composition can be modeled using projection and intersection. Furthermore, the verification problem, namely whether every possible behavior of an implementation is a member of the set of behaviors allowed by the specification, becomes the language-inclusion problem. For Buchi automata, there are known effective constructions for intersection and complementation. Also, the language-inclusion problem is decidable.

For a large class of systems, namely real-time systems, the system has to meet certain hard real-time constraints, for example "the system should respond within 2 seconds", and the correctness of the system depends on the actual values of the delays. For the analysis of such systems, we need to develop formalisms for quantitative temporal reasoning. System designers have realized the need for such models, and several ways to extend the existing formalisms have been suggested. Most of these attempts are tailored to specific applications and do not handle concurrency in a general way. Also, this work is generally somewhat ad hoc: questions such as formal semantics, soundness, expressiveness, and closure properties have not been addressed. This problem has received relatively little attention from theoreticians, though recently researchers have studied quantitative temporal logics ([JM86, Ko89, AH90, ACD90, Le90]).

The first question to address is how to incorporate time explicitly in the underlying formal semantics for processes. Most of the previous work on modeling real-time systems has used two basic approaches. Discrete-time models use the domain of integers to model time. This approach requires that continuous time be approximated by choosing some fixed quantum *a priori*, which limits the accuracy with which the system can be modeled. The fictitious-clock approach introduces a special `tick` transition in the model. Here time is viewed as a global state variable that ranges over the domain of natural numbers and is incremented by one with every `tick` transition (e.g. [AK83, AH90]). This model allows arbitrarily many transitions of any process between two successive `tick` transitions. The timing delay between two events is measured by counting the number of `tick`s between them. Consequently, it is impossible to state precisely certain simple requirements on delays, such as "the delay between two transitions equals 2 seconds." Both models are used, despite their apparent inaccuracy, because they are straightforward extensions of existing temporal models.

In this paper we use a different model. We choose a dense domain to model time and extend the trace semantics by associating with each event its time of occurrence. This allows an unbounded number of environment events between any two events of a system, and also allows a more accurate modeling of the timing delays in asynchronous systems.

To model finite-state real-time systems, we define timed automata. A timed automaton is an $\omega$-automaton with an auxiliary finite set of clocks that record the passage of time. The clocks can be reset with any state transition of the automaton. The timing constraints are expressed by associating enabling conditions with transitions; these conditions compare clock values with time constants. When coupled with acceptance criteria such as Buchi acceptance, timed automata accept timed traces, that is, sequences in which every element has an associated real-valued time.

Our work is based on the recent proposals by Dill ([Di89]) and Lewis ([Le89]) for extending state graphs with timing constraints based on a continuous model of time. These papers provide a way of using timing assumptions to verify qualitative temporal requirements. Later works use these models as interpretations for formulas of branching-time real-time logics, and give model-checking algorithms ([ACD90, Le90]).

In this paper we use timed automata to define languages of linear timed traces, and study their language-theoretic properties. We show that the class of languages accepted by timed Buchi automata (TBA) is closed under intersection and projection. Consequently, there are effective constructions for operations such as parallel composition, hiding, and renaming for processes modeled as sets of timed traces in this class.

Given a TBA, we show how to construct a Buchi automaton that accepts exactly those traces to which times can be attached consistently with the timing constraints of the given automaton. This gives an algorithm for deciding emptiness of its language, and allows the timing-delay information to be used for verifying qualitative temporal requirements. However, the language-inclusion problem is undecidable, which poses difficulties for automatic verification of real-time requirements. We define the notion of determinism for timed automata, and show that deterministic timed automata can be complemented. In particular, we show that deterministic timed Muller automata...

The available preview PDF ends here, in the middle of the final sentence above.
