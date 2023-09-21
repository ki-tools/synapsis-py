#!/usr/bin/env python3

from __future__ import annotations
import typing as t
import sys
import os
import glob
import shutil
import subprocess
import ast

bin_dir = os.path.dirname(__file__)
root_dir = os.path.abspath(os.path.join(bin_dir, '..'))
package_dir = os.path.abspath(os.path.join(root_dir, 'src', 'synapsis'))
stubs_dir = os.path.abspath(os.path.join(bin_dir, 'stubs'))
sys.path.append(root_dir)


def read_file(path: str) -> None:
    with open(path, mode='r') as f:
        return f.read()


def write_file(path: str, content: str) -> None:
    with open(path, mode='w') as f:
        return f.write(content)


def delete_stubs() -> None:
    for dir in [os.path.join(bin_dir, '.mypy_cache'), os.path.join(bin_dir, '.ruff_cache'), stubs_dir]:
        if os.path.isdir(dir):
            shutil.rmtree(dir)


def extract_pyi_methods(contents: str, only: t.Optional[list[str]] = []) -> list[tuple[str, str]]:
    methods = []
    for line in [l.strip() for l in contents.splitlines()]:
        if line.startswith('def ') or line.startswith('async def '):
            name = line.replace('async def ', '', 1).replace('def ', '', 1).split('(')[0]
            if only and name not in only:
                continue
            methods.append((name, line))
    return methods


def is_import_line(line: str) -> bool:
    return line.strip().startswith('import ') or (line.startswith('from ') and ' import ' in line)


def extract_imports(contents: str, root: str = None) -> list[str]:
    imports = []
    for line in contents.splitlines():
        if is_import_line(line) and '_typeshed' not in line:
            if line.startswith('from .') and root is not None:
                line = line.replace('from .', 'from {0}.'.format(root))
            imports.append(line)
    return imports


def build_pyi(target_pyi: str,
              class_name: str,
              method_stubs: dict[str, str],
              imports: t.Optional[list[str]] = None
              ) -> str:
    new_lines = []

    if os.path.isfile(target_pyi):
        target_pyi = read_file(target_pyi)

    target_imports = extract_imports(target_pyi)
    for i in imports:
        if i not in target_imports:
            target_imports.append(i)

    reading_imports = False
    reading_class = False
    source_lines = target_pyi.splitlines()
    if source_lines[-1] != '':
        source_lines.append('')
    for line in source_lines:
        if is_import_line(line):
            reading_imports = True
        elif reading_imports and not line:
            reading_imports = False
            for i in target_imports:
                new_lines.append(i)
            new_lines.append('')
            new_lines.append('Incomplete = t.Any')
            new_lines.append('')
            new_lines.append('')
        elif 'class {0}'.format(class_name) in line:
            reading_class = True
            new_lines.append(line)
        elif reading_class and not line:
            for signature in method_stubs.values():
                new_lines.append('    {0}'.format(signature))
            reading_class = False
        else:
            new_lines.append(line)

    if new_lines[-1] != '':
        new_lines.append('')

    return "\n".join(new_lines)


def stub_synapse_utils() -> None:
    print('Generating stubs for synapse_utils...')
    synapse_utils_pyi_stub_path = os.path.join(stubs_dir, 'synapsis', 'synapse', 'synapse_utils.pyi')
    synapseutils_stub_dir = os.path.join(stubs_dir, 'synapseutils')

    synapse_utils_pyi_contents = read_file(synapse_utils_pyi_stub_path)
    synapseutils_init_pyi_stub_contents = read_file(os.path.join(synapseutils_stub_dir, '__init__.pyi'))

    modules = []
    for node in ast.iter_child_nodes(ast.parse(synapseutils_init_pyi_stub_contents)):
        if isinstance(node, ast.ImportFrom):
            module_name = node.module
        elif isinstance(node, ast.Import):
            alias = node.names[0]
            module_name = alias.asname if alias.asname else alias.name
        else:
            continue

        # Only include imports for synapseutils.
        module_source_path = os.path.join(synapseutils_stub_dir, '{0}.pyi'.format(module_name))
        if not os.path.isfile(module_source_path):
            continue

        if isinstance(node, ast.ImportFrom):
            methods = [m.asname if m.asname else m.names for m in node.names]
            modules.append((module_name, methods))
        elif isinstance(node, ast.Import):
            modules.append((module_name, []))

    method_stubs = {}
    module_imports = []
    for module_name, method_names in modules:
        module_pyi_file = read_file(os.path.join(synapseutils_stub_dir, '{0}.pyi'.format(module_name)))
        for name, signature in extract_pyi_methods(module_pyi_file, only=method_names):
            signature = signature.replace('(syn', '(self')
            if name in method_stubs:
                raise KeyError('method already exists: {0}'.format(name))
            method_stubs[name] = signature
            for i in extract_imports(module_pyi_file, root='synapseutils'):
                if i not in module_imports:
                    module_imports.append(i)

    source = build_pyi(synapse_utils_pyi_contents,
                       'SynapseUtils',
                       method_stubs,
                       imports=module_imports)

    synapse_utils_pyi_path = os.path.join(package_dir, 'synapse', 'synapse_utils.pyi')
    write_file(synapse_utils_pyi_path, source)
    subprocess.run('ruff --fix-only --show-fixes {0}'.format(synapse_utils_pyi_path), shell=True)
    print('Successfully generated: {0}'.format(synapse_utils_pyi_path))


def main():
    delete_stubs()
    for file in glob.glob(os.path.join(package_dir, '**', '*.pyi')):
        os.remove(file)
    subprocess.run('stubgen {0} -o {1}'.format(package_dir, stubs_dir), shell=True)
    subprocess.run('stubgen -p {0} -o {1} --export-less'.format('synapseutils', stubs_dir), shell=True)

    stub_synapse_utils()
    delete_stubs()


if __name__ == "__main__":
    main()
