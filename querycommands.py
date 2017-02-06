import argparse
from glob import glob
from os.path import dirname

from jinja2 import Environment, FileSystemLoader


def parse_doc(doc):
    sections = {}
    current_section = None
    for line in doc.split('\n'):
        if line.startswith('Usage:') or line.startswith('Description:') or \
                line.startswith('Example:') or line.startswith('Permission:'):
            # section start
            line_parts = line.split(':')
            section = line_parts[0]
            initial_data = []
            if len(line_parts) > 1:
                line_data = ''.join(line_parts[1:])
                if line_data:
                    initial_data = [line_data.strip()]
            sections.setdefault(section, initial_data)
            current_section = section
        else:
            if not current_section:
                # discard data because there's no section for it
                continue
            # data
            line = line.strip()
            if line:
                sections[current_section].append(line)

    if 'Usage' not in sections:
        return None, None, None
    usage_data = sections['Usage'][0].split(maxsplit=1)
    command = usage_data[0]
    args = usage_data[1] if len(usage_data) > 1 else None
    return command, ' '.join(sections.get('Description', [])), args


def parse(query_docs):
    commands = {}
    for query_file in glob(query_docs):
        with open(query_file, 'r') as f:
            command, description, args = parse_doc(f.read())
            if command is not None and args is not None:
                commands[command] = {
                    'description': description or '',
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
        '-p', '--path',
        help='(globbing) path to serverquerydocs/',
        required=True
    )
    parser.add_argument(
        '-o', '--output', help='Output-path', default='query.html'
    )
    parser.add_argument(
        '-t', '--template', help='Template', default='query.jinja2'
    )
    args = parser.parse_args()
    main(args.path, args.output, args.template)
