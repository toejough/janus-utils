from . import modules
import janus
import inspect
import collections
import sys


def func_handler(function, *, parser, full_args):
    """
    Handle the parsed function call.

    * get args from positionals or defaults
    * verify required args are present
    * convert args to required type
    * get kwargs from options
    * flip any bools as necessary
    * verify required kwargs are present
    * call the function
    """
    # get args from positionals or defaults
    # and verify required args are present
    # and convert args to required type
    for index, name in enumerate(full_args.keys()):
        if full_args[name]['arg type'] == 'positional':
            if index < len(parser.arguments):
                try:
                    full_args[name]['value'] = full_args[name]['type'](parser.arguments[index])
                except ValueError:
                    raise ValueError(f"Could not convert {name} to the target type.")
            elif not full_args[name]['required']:
                full_args[name]['value'] = full_args[name]['default']
            else:
                raise RuntimeError(f"Required arg ({name}) missing!")
    # get kwargs from options
    # flip any bools as necessary
    # verify required kwargs are present
    for name, option in parser.options.items():
        if option.type == 'bool' and name.startswith('not-'):
            full_args[name[4:]]['value'] = not option.value
        else:
            full_args[name]['value'] = option.value
            if option.value is None and full_args[name]['required']:
                raise RuntimeError(f"Required option ({name}) missing!")
    # call the function
    kwargs = {name: data['value'] for name, data in full_args.items()}
    function(**kwargs)


def add_function_parser(parser: janus.ArgParser, *, function):
    try:
        function_doc = [l for l in (function.__doc__ or "\n").splitlines() if l][0]
    except IndexError:
        function_doc = ""
    argspec = inspect.getfullargspec(function)
    # argspec defaults omit args without defaults, so we add Nones there
    all_defaults = [None] * (len(argspec.args or []) - len(argspec.defaults or [])) + list(argspec.defaults or [])
    full_args = collections.OrderedDict()
    # set up args
    for name, default in zip(argspec.args, all_defaults):
        # set var type to the annotated type if annotated,
        # else str if no default, else type of the default
        this_type = argspec.annotations.get(name, str if default is None else type(default))
        if this_type not in (int, float, str):
            raise TypeError("Cannot create CLI for {function.__name__} - unhandled type {this_type} for arg ({name}).")
        full_args[name] = {
            'default': default,
            'type': this_type,
            'required': default is None,
            'arg type': 'positional',
        }
        if full_args[name]['required']:
            function_doc += f"\n  {name} ({this_type.__name__}): required - no default"
        else:
            function_doc += f"\n  {name} ({this_type.__name__}): default is {default}"
    # set up kwargs
    for name in argspec.kwonlyargs:
        default = (argspec.kwonlydefaults or {}).get(name, None)
        this_type = argspec.annotations.get(name, str if default is None else type(default))
        if this_type not in (int, float, str, bool):
            raise TypeError("Cannot create CLI for {function.__name__} - unhandled type {this_type} for arg ({name}).")
        full_args[name] = {
            'default': default,
            'type': this_type,
            'required': default is None,
            'arg type': 'option',
        }
        if full_args[name]['required']:
            function_doc += f"\n  --{name} ({this_type.__name__}): required - no default"
        elif this_type is bool and default is True:
            function_doc += f"\n  --not-{name} ({this_type.__name__}): unless set, {name} will be True"
        else:
            function_doc += f"\n  --{name} ({this_type.__name__}): default is {default}"
    # func parser
    func_parser = parser.new_cmd(function.__name__, helptext=function_doc, callback=lambda p: func_handler(function, parser=p, full_args=full_args))
    # add everything
    for name, data in full_args.items():
        default = data['default']
        this_type = data['type']
        if data['arg type'] == 'option':
            if this_type is int:
                func_parser.new_int(name, fallback=default)
            elif this_type is float:
                func_parser.new_float(name, fallback=default)
            elif this_type is str:
                func_parser.new_str(name, fallback=default)
            elif this_type is bool:
                if default is True:
                    func_parser.new_flag(f"not-{name}")
                else:
                    func_parser.new_flag(name)


def module_callback(parser):
    # the module callback is always called, even if a subcommand
    # was executed.  That's not what we want, so only do the help
    # if there was no subcommand parsed.
    if parser.command is None:
        parser.exit_help()


def add_module_parser(parser, *, module):
    modules = []
    functions = []
    for name, member in inspect.getmembers(module):
        if inspect.ismodule(member):
            modules.append(member)
        elif inspect.isfunction(member):
            functions.append(member)
    if not modules and not functions:
        raise ValueError(f"No functions or modules in {module.__name__} - can't build a CLI parser")
    module_doc = (module.__doc__ or "") + "\n\nCommands:\n  " + "\n  ".join([i.__name__.split('.')[-1] for i in modules + functions])
    subparser = parser.new_cmd(module.__name__.split('.')[-1], helptext=module_doc, callback=module_callback)
    for this_module in modules:
        add_module_parser(subparser, module=this_module)
    for this_function in functions:
        add_function_parser(subparser, function=this_function)


def build_module_parser(*, module, version):
    modules = []
    functions = []
    for name, member in inspect.getmembers(module):
        if inspect.ismodule(member):
            modules.append(member)
        elif inspect.isfunction(member):
            functions.append(member)
    if not modules and not functions:
        raise ValueError(f"No functions or modules in {module.__name__} - can't build a CLI parser")
    module_doc = (module.__doc__ or "") + "\n\nCommands:\n  " + "\n  ".join([i.__name__.split('.')[-1] for i in modules + functions])
    parser = janus.ArgParser(helptext=module_doc, version=version)
    for this_module in modules:
        add_module_parser(parser, module=this_module)
    for this_function in functions:
        add_function_parser(parser, function=this_function)
    return parser


def main():
    parser = build_module_parser(module=modules, version="0.1.0")
    try:
        parser.parse()
    except Exception as e:
        sys.exit(f"Parsing error: {e}")
    if not parser.command:
        parser.exit_help()
