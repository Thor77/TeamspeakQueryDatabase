import argparse
from glob import glob
from os.path import dirname

from jinja2 import Environment, FileSystemLoader


def parse_doc(doc):
    lines = doc.split('\n')
    # blank between usage and description
    first_blank = lines.index('')
    # blank between desc and ex
    next_blank = (first_blank + 1) + lines[first_blank + 1:].index('')
    description = ''.join(lines[first_blank + 1:next_blank])
    args = ' '.join(''.join([args.strip() for args in lines[:first_blank]])
                    .split()[2:])
    return lines[0].split()[1], description, args


def parse(query_docs):
    commands = {}
    for query_file in glob(query_docs):
        with open(query_file, 'r') as f:
            command, description, args = parse_doc(f.read())
            commands[command] = {
                'description': description,
                'arguments': args
            }
    return commands


def render(query_commands, output, template='query.jinja2'):
    template_loader = FileSystemLoader(dirname(__file__))
    template_env = Environment(loader=template_loader)
    template = template_env.get_template(template)
    with open(output, 'w') as f:
        f.write(template.render(
            commands=sorted(query_commands.items(), key=lambda i: i[0])
        ))


def main(query_docs, output, template='query.jinja2'):
    commands = parse(query_docs)
    render(commands, output, template)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Visualize Teamspeak Query-docs')
    parser.add_argument(
        '-qc', '--querycommands',
        help='(globbing) path to query commands',
        required=True
    )
    parser.add_argument(
        '-o', '--output', help='Output-path', default='query.html'
    )
    parser.add_argument(
        '-t', '--template', help='Template', default='query.jinja2'
    )
    args = parser.parse_args()
    main(args.querycommands, args.output, args.template)
