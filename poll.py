from errbot import botcmd, BotPlugin

from pollentry import PollEntry


class Poll(BotPlugin):
    def activate(self) -> None:
        super().activate()

        # initial setup
        if 'current_poll' not in self:
            self['current_poll'] = None
        if 'polls' not in self:
            self['polls'] = {}

    @botcmd
    def poll_new(self, _, title) -> str:
        """Create a new poll.
        usage: !poll new <poll_title>
        """
        if not title:
            return 'usage: !poll new <poll_title>'

        if title in self['polls']:
            return 'A poll with that title already exists.'

        with self.mutable('polls') as polls:
            polls[title] = PollEntry()

        if not self['current_poll']:
            self['current_poll'] = title

        return 'Poll created. Use !poll option to add options.'

    @botcmd
    def poll_remove(self, _, title) -> str:
        """Remove a poll."""
        if not title:
            return 'usage: !poll remove <poll_title>'

        with self.mutable('polls') as polls:
            try:
                del polls[title]
            except KeyError as _:
                return 'That poll does not exist. Use !poll list to see all polls.'
        return 'Poll removed.'

    @botcmd
    def poll_list(self, *_) -> str:
        """List all polls."""
        if self['polls']:
            return 'All Polls:\n' + \
                   '\n'.join([title + (' *' if title == self['current_poll'] else '') for title in self['polls']])
        return 'No polls found. Use !poll new to add one.'

    @botcmd
    def poll_start(self, _, title) -> str:
        """Start a saved poll."""
        if self['current_poll']:
            return '"{}" is currently running, use !poll end to finish it.'.format(self['current_poll'])

        if not title:
            return 'usage: !poll start <poll_title>'

        if title not in self['polls']:
            return 'Poll not found. Use !poll list to see all polls.'

        self.reset_poll(title)
        self['current_poll'] = title

        return '{}:\n{}'.format(title, str(self['polls'][title]))

    @botcmd
    def poll_end(self, *_) -> str:
        """Stop the currently running poll."""
        current_poll = self['current_poll']
        if not current_poll:
            return 'There is no active Poll.'

        result = 'Poll finished, final results:\n'
        result += str(self['polls'][current_poll])

        self.reset_poll(current_poll)
        self['current_poll'] = None
        return result

    @botcmd
    def poll_option(self, _, option) -> str:
        """Add an option to the currently running poll."""
        current_poll = self['current_poll']
        if not current_poll:
            return 'No active poll. Use !poll start to start a poll.'

        if not option:
            return 'usage: !poll option <poll_option>'

        with self.mutable('polls') as polls:
            poll = polls[current_poll]

            if option in poll.options:
                return 'Option already exists. Use !poll show to see all options.'

            poll.options[option] = 0

            return '{}:\n{}'.format(current_poll, poll)

    @botcmd
    def poll(self, *_) -> str:
        """Show the currently running poll."""
        current_poll = self['current_poll']

        if not current_poll:
            return 'No active poll. Use !poll start to start a poll.'

        return '{}:\n{}'.format(current_poll, self['polls'][current_poll])

    @botcmd
    def vote(self, msg, index) -> str:
        """Vote for the currently running poll."""
        current_poll = self['current_poll']
        if not current_poll:
            return 'No active poll. Use !poll start to start a poll.'

        if not index:
            return 'usage: !vote <option_number>'

        if not index.isdigit():
            return 'Please vote using the numerical index of the option.'

        with self.mutable('polls') as polls:
            poll = polls[current_poll]
            index = int(index)
            if index > len(poll.options) or index < 1:
                return 'Please choose a number between 1 and {} (inclusive).'.format(poll.options.len)

            option = sorted(poll.options.keys())[index - 1]

            if option not in poll.options:
                return 'Option not found. Use !poll show to see all options of the current poll.'

            if msg.frm in poll.has_voted:
                return 'You have already voted.'

            poll.has_voted.append(msg.frm)

            poll.options[option] += 1

            return '{}:\n{}'.format(current_poll, poll)

    def reset_poll(self, title) -> None:
        with self.mutable('polls') as polls:
            poll = polls[title]
            for option in poll.options:
                poll.options[option] = 0
            del poll.has_voted[:]
