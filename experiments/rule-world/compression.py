"""Compression-based analog baseline.

A small PPM-style (Prediction by Partial Matching) context model over the
substance/property table. Different mathematical foundation from HDC:
instead of high-dimensional binary vectors with bind/bundle, this is
classical frequency-based prediction with no matrix multiplication, no
floating-point ops, only integer counters.

The idea: for each property, count which substances exhibit it. To
predict the analog of a new substance, look up its properties and
aggregate the substance frequencies. This is the prediction-compression
duality applied to a tiny domain.

If this baseline produces the same analogs as HDC v3/v4 on the
adversarial scenarios, that is evidence that **grounded analogy is a
property of the right representation, not an artifact of HDC
specifically**. It would localize what we built in HDC to a more
general mathematical phenomenon.

Operations: dict lookup, integer increment, Counter.most_common.
Complexity: O(P) per query where P = number of properties on the new
substance. Memory: O(unique_properties × unique_substances). Both
trivially smaller than any matmul.
"""

from __future__ import annotations

from collections import Counter


class CompressionAnalog:
    """A frequency-based analog predictor over a property table.

    Built from the same SUBSTANCE_PROPERTIES table that HDC uses, so the
    only difference between this and HDC is the math: HDC computes
    similarity by dot-product of bipolar vectors; compression computes it
    by tallying property co-occurrences.
    """

    def __init__(self, property_table: dict[str, list[str]]):
        # property -> Counter({substance: count})
        self.property_index: dict[str, Counter] = {}
        for substance, props in property_table.items():
            for p in props:
                self.property_index.setdefault(p, Counter())[substance] += 1
        self.property_table = property_table

    def predict(
        self,
        query_substance: str,
        query_properties: list[str],
        exclude_self: bool = True,
    ) -> list[tuple[str, int]]:
        """Return ranked analog candidates by aggregate property frequency.

        Output: list of (substance, score) sorted descending. Score is the
        number of (property, substance) co-occurrences from `query_properties`
        across the index, excluding the query substance itself.
        """
        scores: Counter = Counter()
        for prop in query_properties:
            if prop not in self.property_index:
                continue
            for sub, count in self.property_index[prop].items():
                if exclude_self and sub == query_substance:
                    continue
                scores[sub] += count
        return scores.most_common()

    def predict_role_weighted(
        self,
        query_substance: str,
        query_properties: list[str],
        property_roles: dict[str, str],
        active_roles: set[str],
        exclude_self: bool = True,
    ) -> list[tuple[str, int]]:
        """Same as predict, but only counts properties whose role is active.

        This is the compression-side analog of HDC's role-weighted
        encoding (v3/v4). Tests whether the role-filtering gain is
        substrate-agnostic.
        """
        filtered = [
            p for p in query_properties
            if property_roles.get(p) in active_roles
        ]
        return self.predict(query_substance, filtered, exclude_self=exclude_self)
