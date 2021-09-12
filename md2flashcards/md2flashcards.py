import argparse
from typing import Any
from typing import NamedTuple
from typing import Optional
from typing import Sequence

import mistune
from mistune.plugins import plugin_def_list


def _create_argparser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'mdfile',
        help='the markdown file to extract the flashcards from',
    )
    parser.add_argument(
        'outfile',
        help='the (csv) file to write the flaskcards to',
    )
    return parser


def _create_md_ast(filepath: str) -> list[dict[str, Any]]:
    with open(filepath, 'r') as file:
        file_content = file.read()

    ast_renderer = mistune.AstRenderer()
    create_ast = mistune.create_markdown(
        escape=False,
        renderer=ast_renderer,
        plugins=[plugin_def_list],
    )

    return create_ast(file_content)


class DefinitionList(NamedTuple):
    header: str
    definitions: list[str]

    def to_tsv(self) -> str:
        if len(self.definitions) == 1:
            def_str = self.definitions[0]
        else:
            def_str = ''.join(
                [
                    f'Definition {i}: {d} ' for i,
                    d in enumerate(self.definitions)
                ],
            )

        return f'{self.header}\t{def_str}\n'


def _find_definition_lists(ast: list[dict[str, Any]]) -> list[DefinitionList]:

    def_lists: list[DefinitionList] = []
    for node in ast:
        if node['type'] == 'def_list':
            header = ''
            defs = []
            if 'children' in node:
                for child_node in node['children']:
                    if child_node['type'] == 'def_list_header':
                        header = child_node['text']
                    if child_node['type'] == 'def_list_item':
                        defs.append(child_node['text'])

                def_lists.append(
                    DefinitionList(header, defs),
                )

    return def_lists


def _save_tsv_file(filepath: str, items: list[str]) -> None:

    with open(filepath, 'w') as tsv_file:
        tsv_file.writelines(items)


def main(argv: Optional[Sequence] = None) -> int:

    parser = _create_argparser()
    args = parser.parse_args(argv)
    ast = _create_md_ast(args.mdfile)

    def_lists = _find_definition_lists(ast)

    _save_tsv_file(args.outfile, [df.to_tsv() for df in def_lists])

    return 0
