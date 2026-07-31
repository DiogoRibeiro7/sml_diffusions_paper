# Final revision issue matrix

Every issue raised in the third review round, with its resolution. Branch `fix/final-mathematical-review`,
baseline commit `0cbc760`.

Severity: **blocking** means a false or unsupported mathematical statement; **major** means a claim
wider than its support; **minor** means an ambiguity that could mislead; **editorial** means
presentation only.

| # | Issue | Severity | Files | Claims affected | Resolution | Tests |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Proposition E.2 missing the Moore–Penrose magnitude condition | **blocking** | `main.tex` §E.3 | PSD characterisation in the degenerate configuration; §1 sixth contribution; §8.1(iv); conclusion | New Lemma E.1 proved from scratch (both directions); Proposition E.2 restated with conditions (i) and (ii); the false inference deleted; explicit numerical counterexample added | `tests/test_singular_psd_condition.py`, 16 tests |
| 2 | Every correlation claimed automatically bounded | **major** | `main.tex` §1, §8.1(iv), §E | scope of Proposition E.1 | Proposition E.1 retitled and its scope stated in the statement itself; new Table 11 classifying all seven correlations; "not redundant on the five free parameters" stated | forbidden-phrase gate |
| 3 | Grid sweep described as the reachable state space | **major** | `main.tex` §E.1, §8.1(iv), conclusion; `dist/application_feasibility_matrix.md` | the 66 per cent claim and everything drawing on it | §E.1 renamed "Algebraic domain of the state transformation"; explicit list of what the grid does not establish; percentages replaced by counts; six-design sensitivity table added; limitations paragraph naming what reachability would require | `run_grid_sensitivity`, forbidden-phrase gate |
| 4 | Proposition 6.2 does not localise the simulated maximiser | **blocking** | `main.tex` §6 | abstract equivalence result; §1.2 classification | Restated with six hypotheses including consistency of both maximisers and segment containment; full proof written using the integral form of the mean-value theorem; Remark 6.3 records where localisation must come from | claim matrix |
| 5 | Proposition F.1 refers to "defining constraints" without a representation | **major** | `main.tex` §F | corner-solution argument | Constraint representation \eqref{eq:constraint_representation} fixed with finite `J` and continuous `g_j`; compactness proved; the active-constraint alternative stated explicitly and proved by contradiction | `tests/test_analytics.py` |
| 6 | Binding-constraint conclusion too strong for the time-varying models | **major** | `main.tex` §F, §8.1(v), conclusion | `min_t eps^2 = 0` for all specifications | Split into three statuses: exact theorem for the constant case, reported empirical fact for the time-varying cases, conditional for the enlarged feasible set. "We cannot independently determine the active constraint" stated plainly | — |
| 7 | Direct-`H` Euler analysis read as evidence about the implemented chain | **major** | `main.tex` §1, §8.1(i)–(ii), §9.5, App. C, conclusion | boundary-crossing claims | Explicit establishes/does-not-establish lists added before Proposition C.1; what an implemented-chain analysis would require enumerated; conclusion no longer says the chain fails | forbidden-phrase gate |
| 8 | Shrinking dangerous region said to reduce occupation | **blocking** | `main.tex` App. C | interpretation after Proposition C.1 | Replaced with the five-quantity list (a)–(e); the integrated failure probability written as `∫ P_h dπ_h` with a statement that `π_h` is not analysed; the multiplication fallacy for path risk named | forbidden-phrase gate |
| 9 | `S` redefined in the antithetic subsection | **major** | `main.tex` §8.2, Table 3 | effective-size accounting | `P` pairs and `E = 2P` evaluations introduced for that subsection only; variance formula \eqref{eq:antithetic_variance} proved | `tests/test_antithetic.py` |
| 9a | Variance-equivalent count misread, introduced by the fix for issue 9 | **major** | `main.tex` §8.2, Table 3 | `E` versus `N_eff` versus `P` | The fix claimed `E` overstates the count by `2/(1+ρ_A)`, "exactly two at a coincident endpoint": wrong factor, and that expression equals one at `ρ_A = 1`. `N_eff = E/(1+ρ_A)` now defined, both ratios written out, four cases stated, `R_pair` and `R_var` separated, Table 3 reporting `R_var` at two reference `ρ_A`, and new Lemma 8.2 proving the `h^{−K/2}` exponent survives pairing | `tests/test_antithetic.py`, 26 tests; 3 new forbidden-phrase patterns |
| 10 | Milstein bandwidth/covariance wording | minor | `main.tex` §1.1 | the `K/2` exponent argument | Reconstructed from the source: kernel written out from their eq. (1.5), covariance `b²I` and bandwidth `b` stated separately, both conventions given side by side | — |
| 11 | Prior-literature notation collision | **major** | `main.tex` §1.1, Table 1 | every quoted rate | Neutral symbols `n_data`, `n_MC`, `m_Euler`, `b_ker` introduced with a translation note; footnotes record original symbols; Detemple's `M` identified as this paper's `S`; Table 1 fully translated with an "Error quantity" column | — |
| 12 | Missing pinpoint citations | minor | `main.tex` §1.1 | attributed quotations | Every direct quotation now carries a page and, where available, a theorem, figure or equation number | — |
| 13 | René Garcia rendering | **major** | `references.bib` | bibliography | The `.bib` held `Ren{'e}` with the backslash lost, and the PDF rendered "Ren'e Garcia". Corrected to `Ren{\'e}`; verified in the compiled PDF as `Ren\351` | forbidden-phrase gate |
| 14 | Figure 5 floating into the conclusion | editorial | `main.tex` | layout | `placeins` loaded, `\FloatBarrier` before every section and before the conclusion | float audit |
| 15 | End-loaded tables | editorial | `main.tex` | layout | Worse than reported: Table 1 was cited on page 3 and placed on page 31. All floats changed from `[t]` to `[htbp]` and the float parameters relaxed; Table 1 now lands on page 7 | float audit |
| 16 | Table 9 matrix count ambiguity | minor | `main.tex` §E.1 | `38,496` matrices | Caption states `38,496 = 2 × 19,248`; column renamed "Branch-specific matrices" | — |
| 17 | Affiliation formatting | editorial | `main.tex`, `CITATION.cff`, `.zenodo.json` | front matter | Expanded on the author's instruction, and later set by the author to the English form `School of Media Arts and Design, Polytechnic of Porto` | metadata gate, consistency test |

## The affiliation

Prompt 10 Part B asks for the official institutional name, verified from an authoritative source
"already documented by the author or repository". At the time of the first pass no such source
existed here: `ESMAD -IPP` had been supplied as an acronym and nothing corroborated an expansion, so
the field was left unchanged rather than guessed at.

The author supplied the expansion, then the plural *Escola Superior de Media Artes e Design*, and
finally set the field to the English form **School of Media Arts and Design, Polytechnic of Porto**.
The last is what the manuscript now carries, and the other files follow it.

The consistency test earned its place here. The English form was entered in `main.tex` alone, and the
test in `tests/test_analytics.py` failed on the next run, naming the exact string that no longer
matched. Without it, `CITATION.cff` and `.zenodo.json` would have kept the Portuguese form silently,
and the divergence would have surfaced only in a published Zenodo record.

One consequence is worth recording: the v1.0.0 Zenodo record was minted before this change and
carries *Escola Superior de Media Artes e Design, IPP*. Zenodo records are immutable once published,
so that version keeps the Portuguese form; the next release will carry the English one. The concept
DOI resolves to the newest version, so a reader following the citation sees the current form.

## Rules observed

- The Brownian counterexample, exact moments, local moment theorem and corrected triangular-array
  CLT are untouched. No error was found in them in this round.
- No new claim was introduced to preserve older wording. Where support was absent, the statement was
  narrowed: issues 3, 6, 7 and 8 are all narrowings.
- Every numerical statement in the manuscript is generated by code in `code/` and reproduced
  bit-for-bit by `make verify`.
- Each application claim is classified in `docs/final_claim_dependency_audit.md`.
