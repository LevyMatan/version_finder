# core/parsers/core_scope_parser.py
from semantic_release.commit_parser import AngularCommitParser
from semantic_release.enums import LevelBump
from semantic_release.commit_parser.token import ParsedMessageResult

class CustomCommitParserFilterByScopeCore(AngularCommitParser):
    def parse_message(self, message: str) -> ParsedMessageResult | None:
        parsed = super().parse_message(message)
        if parsed is None:
            return None

        # Only change version level if scope is not 'core'
        if parsed.scope and "core" not in parsed.scope:
            parsed = parsed._replace(bump=LevelBump.NO_RELEASE)

        return parsed


class CustomCommitParserFilterByScopeGui(AngularCommitParser):
    def parse_message(self, message: str) -> ParsedMessageResult | None:
        parsed = super().parse_message(message)
        if parsed is None:
            return None

        # Only change version level if scope is not 'core'
        if parsed.scope and "gui" not in parsed.scope:
            parsed = parsed._replace(bump=LevelBump.NO_RELEASE)

        return parsed


class CustomCommitParserFilterByScopeCli(AngularCommitParser):
    def parse_message(self, message: str) -> ParsedMessageResult | None:
        parsed = super().parse_message(message)
        if parsed is None:
            return None

        # Only change version level if scope is not 'core'
        if parsed.scope and "cli" not in parsed.scope:
            parsed = parsed._replace(bump=LevelBump.NO_RELEASE)

        return parsed