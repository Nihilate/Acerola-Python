from ordered_set import OrderedSet

from .util import find_closest


class Searcher:
    def __init__(self, sources, consolidator=None):
        self._potential_sources = sources
        self._active_sources = {}
        self._consolidator = consolidator

    def add_source(self, *args):
        for source_type in args:
            try:
                self._active_sources[source_type] = self._potential_sources[source_type]
            except KeyError:
                raise ValueError(str(source_type) + ' is not a valid source for this series type.')

    def search_all(self, search_term):
        results = {}

        for source_type in self._active_sources.keys():
            results[source_type] = self._active_sources[source_type](search_term)

        return results

    # TODO - implement a depth limit?
    # todo re-engineer
    def search_closest(self, search_term):
        relevant_terms = OrderedSet()
        relevant_terms.add(search_term.lower())

        results = {source_type: SearchResults() for source_type in self._active_sources.keys()}

        while True:
            valid_sources = {source_type: results[source_type] for source_type in results.keys()
                             if results[source_type].chosen_result is None
                             and results[source_type].checked_terms != relevant_terms}

            if not valid_sources:
                break

            for source_type in [source_type for source_type, search_results in valid_sources.items()]:
                results_for_source = valid_sources[source_type]

                unseen_terms = [term for term in relevant_terms if term not in results_for_source.checked_terms]

                for term in unseen_terms:
                    closest_in_current_results = find_closest(term, valid_sources[source_type].results_cache)

                    if closest_in_current_results:
                        results_for_source.chosen_result = closest_in_current_results
                    else:
                        new_results = self._active_sources[source_type](term)
                        results_for_source.results_cache.update(new_results)

                        closest_in_new_results = find_closest(term, valid_sources[source_type].results_cache)

                        if closest_in_new_results:
                            results_for_source.chosen_result = closest_in_new_results

                    results_for_source.checked_terms.add(term)

                    if results_for_source.chosen_result:
                        if results_for_source.chosen_result.title_english:
                            relevant_terms.add(results_for_source.chosen_result.title_english.lower())

                        if results_for_source.chosen_result.title_romaji:
                            relevant_terms.add(results_for_source.chosen_result.title_romaji.lower())

                        relevant_terms.update([synonym.lower() for synonym in results_for_source.chosen_result.synonyms])
                        break

        chosen_results = {source_type: results[source_type].chosen_result
                          for source_type, search_results in results.items()}

        return chosen_results

    def consolidate(self, list_of_response_objects):
        return self._consolidator(list_of_response_objects)


class SearchResults:
    def __init__(self):
        self.checked_terms = set()
        self.results_cache = OrderedSet()
        self.chosen_result = None
