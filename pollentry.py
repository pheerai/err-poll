from typing import Mapping, List

from errbot.backends.base import Identifier


class PollEntry(object):
    """
    This is just a data object that can be pickled.
    """
    def __init__(self):
        self._options = {}
        self._has_voted = []

    @property
    def options(self) -> Mapping[str, int]:
        return self._options

    @property
    def has_voted(self) -> List[Identifier]:
        return self._has_voted

    def __str__(self) -> str:
        total_votes = sum(self._options.values())

        result = ''
        keys = sorted(self._options.keys())
        for index, option in enumerate(keys):
            votes = self._options[option]
            result += '{} {}. {} ({} votes)\n'.format(drawbar(votes, total_votes), index+1, option, votes)

        return result.strip()


def drawbar(value, max_) -> str:
    if max_:
        value_in_chr = int(round((value * BAR_WIDTH / max_)))
    else:
        value_in_chr = 0
    return '[' + '█' * value_in_chr + '▒' * int(round(BAR_WIDTH - value_in_chr)) + ']'


BAR_WIDTH = 15.0
