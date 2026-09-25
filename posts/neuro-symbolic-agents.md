# Neuro-Symbolic Agents: From Plausible Answers to Supported Claims

*Combining neural interpretation, ontologies, and evidence-backed inference.*

An agent tells you: “Abebe has a defaulted loan.”

The sentence sounds reasonable. But did the agent understand which Abebe you meant? Does its interpretation fit your domain? And does a record actually support the claim?

These are three different questions. A useful architecture should not collapse them into one confidence score.

**Neuro-symbolic inference separates the work: a neural model interprets language, while symbolic components check structure and derive conclusions.** Systems such as Logic-LM demonstrate this division by translating natural-language problems into formal representations for symbolic solvers. [1]

Here is a compact framework for applying that idea to an ontology-grounded agent.

## 1. Turn language into a structured question

Suppose a user asks:

> Does Abebe have a defaulted loan?

A neural model maps the input $x$ into a representation $h$, then proposes a symbolic interpretation $z$:

$$
h = f_\theta(x),
\qquad
z \sim p_\theta(z \mid h, \mathcal O)
$$

Here, $\theta$ denotes model parameters and $\mathcal O$ is the ontology. This is a conceptual decomposition, not a requirement for separate encoder and parser models.

Assuming entity resolution identifies Abebe as `customer_17`, the interpretation could be:

```text
EXISTS loan:
    hasLoan(customer_17, loan)
    AND DefaultedLoan(loan)
```

Notice what the model has produced: **a question to execute, not a fact to believe.**

This is an operational meaning of “understanding”: mapping an input to an explicit, testable interpretation. It does not establish human-like comprehension. If two customers match “Abebe,” the agent still needs to resolve that ambiguity.

## 2. Separate the ontology from the evidence

Let $\mathcal O$ contain domain concepts, relationships, and logical axioms. Let $D$ contain accepted facts retrieved from the relevant records. Their combination is the knowledge base:

$$
K = \mathcal O \cup D
$$

Ontologies can describe relationships and support deductions; they do not automatically establish that a particular real-world event occurred. [2]

For our example, define the relationship signature:

```text
hasLoan: Customer × Loan
```

And two logical rules, with variables universally quantified:

$$
\begin{aligned}
\operatorname{DefaultedLoan}(l)
&\Rightarrow \operatorname{Loan}(l) \\
\operatorname{Customer}(c) \land \operatorname{hasLoan}(c,l)
\land \operatorname{DefaultedLoan}(l)
&\Rightarrow \operatorname{HasDefaultedLoan}(c)
\end{aligned}
$$

Now suppose the retrieved evidence contains:

```text
Customer(customer_17)
hasLoan(customer_17, loan_42)
DefaultedLoan(loan_42)
DefaultedLoan(loan_99)
```

The rule derives `HasDefaultedLoan(customer_17)`. The answer can identify `loan_42` and attach the supporting record references.

But `loan_99` being a defaulted loan does not establish that Abebe holds it. That claim is compatible with the ontology, yet no supplied fact links this customer to that loan.

**Consistency asks whether a claim could fit the knowledge base. Entailment asks whether it follows from the knowledge base.** They are not interchangeable. [2]

## 3. Make inference a constrained optimization problem

Let $y$ be a structured candidate answer, and let $\operatorname{Claims}(y)$ be its factual assertions. Define $V(y)=1$ when it passes explicitly implemented schema and type checks.

Assuming $K$ is logically consistent, define the admissible answers:

$$
\mathcal Y_{\mathrm{adm}}
=
\left\{
 y \in \mathcal Y
 \;\middle|\;
 V(y)=1
 \;\land\;
 \forall c \in \operatorname{Claims}(y),\; K \models c
\right\}
$$

The notation $K \models c$ means that $c$ logically follows from $K$. [2]

Then choose:

$$
\boxed{
y^*
=
\underset{y \in \mathcal Y_{\mathrm{adm}}}{\arg\max}
\; p_\theta(y \mid x,K)
}
$$

In plain English: **choose the model’s preferred answer, but only among structurally valid, evidence-supported candidates.**

Imagine two candidates receive hypothetical proposal probabilities:

| Candidate answer | Neural probability | Structurally valid? | Supported by $K$? |
| --- | ---: | --- | --- |
| Abebe has defaulted loan `loan_99`. | 0.65 | Yes | No |
| Abebe has defaulted loan `loan_42`. | 0.35 | Yes | Yes |

Unconstrained selection prefers the first. The constrained system rejects it and selects the second.

The numbers are illustrative, not measured confidence estimates. In practice, a system can generate and validate a finite candidate set rather than search every possible answer. If none qualify, it should retrieve more evidence or abstain.

**Implementation matters:** OWL domain and range axioms can infer types rather than reject malformed data. Use explicit validation—such as SHACL for RDF graphs—when rejection is required. Ontology axioms are not automatically database constraints. [2][3]

## 4. Combine soft preferences with hard boundaries

Not every preference needs an absolute rule. A system might prefer simpler interpretations while still requiring factual support.

One illustrative formulation is:

$$
q(y \mid x,K)
=
\frac{1}{Z}
\,p_\theta(y \mid x,K)
\,e^{-\lambda S(y)}
\,\mathbf 1[y \in \mathcal Y_{\mathrm{adm}}]
$$

Here, $S(y)\geq 0$ penalizes undesirable properties, $\lambda\geq 0$ controls that penalty, and $Z$ normalizes the distribution. If $Z=0$, no supported proposal has positive probability: abstain or gather more evidence.

The neural model ranks possibilities. The penalty adjusts preferences. The indicator enforces the boundary.

This connects to the broader idea of constraining probabilistic models; posterior regularization is an established related framework, although its learning objective differs from this illustrative inference rule. [4]

Importantly, **$q$ is a selection distribution, not a calibrated probability of real-world truth.** Filtering candidates cannot turn unreliable evidence into certainty.

## 5. What the framework does—and does not—guarantee

With a sound checker, a consistent knowledge base, and complete enforcement, every accepted formal claim follows from the supplied premises. That is a meaningful but conditional guarantee.

It does not guarantee that the records are correct, that “Abebe” was resolved correctly, or that the ontology captures the intended business meaning. A perfect deduction from a wrong premise can still produce a wrong answer.

Missing evidence also does not prove the opposite. Under OWL’s open-world semantics, an absent fact may simply be unknown. “I found no defaulted loan in the available records” is different from “Abebe has no defaulted loans.” [2]

Finally, the language-generation step must not add unverified details. For strict outputs, render validated claims through templates or check the final response against those claims. Keep source identifiers and timestamps with the evidence.

A practical design is:

```text
User input → Neural interpretation → Query validation
           → Evidence retrieval → Symbolic inference
           → Claim validation → Faithful response
```

The goal is not to give an agent an ontology and declare it incapable of hallucination. It is to make unsupported assertions fail an explicit acceptance test.

**Let the neural model propose what the input means. Let the ontology define its structure. Let the evidence determine what the agent may assert.**

---

## References

[1] Pan et al. (2023). [Logic-LM: Empowering Large Language Models with Symbolic Solvers for Faithful Logical Reasoning](https://arxiv.org/abs/2305.12295).

[2] W3C (2012). [OWL 2 Web Ontology Language Primer, Second Edition](https://www.w3.org/TR/owl2-primer/). See the discussions of entailment, open-world semantics, and domain/range axioms.

[3] W3C (2017). [Shapes Constraint Language (SHACL)](https://www.w3.org/TR/shacl/).

[4] Ganchev et al. (2010). [Posterior Regularization for Structured Latent Variable Models](https://www.jmlr.org/papers/v11/ganchev10a.html). *Journal of Machine Learning Research*, 11, 2001–2049.
