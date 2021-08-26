import datetime
import io
import sys
import typing

DEFAULT_STREAM = sys.stdout


def _default_skip_predicate(name: str, value: typing.Any, callable_=callable) -> bool:
    return name.startswith('_') or value is None or callable_(value)


def bprint(
        *values: typing.Any,
        stream: typing.Union[typing.TextIO, typing.Type[str]] = None,
        indent: typing.Union[str, typing.Tuple[str]] = '  ',
        start_indent_level: int = 0,
        maximum_depth: int = None,
        sort=True,
        max_str_len=256,
        max_bytes_len=64,
        truncate_suffix='…',
        human_bytes=True,
        skip_predicate: typing.Callable[[str, typing.Any], bool] = _default_skip_predicate,
        seq_bullet='- ',
        sep='\n\n',
        inline_singular=False
):
    """
    Beautifully prints the given ``values``.
    Arguments
        values
            The object or objects to beautifully print.
        stream
            The output stream where the method should print to.
            If it's ``str``, it will be written to memory,
            and the printed results will be returned as a string.
        indent
            The string used for each indent level.
            If a tuple of two strings is passed, the first string
            will be used for the first indent, and the second string
            for the rest.
            If a tuple of three strings is passed, the first string
            will be used for the first indent, the third for the last,
            and the second for the rest.
        start_indent_level
            The starting indent level.
        maximum_depth
            The maximum depth to print. By default, all nesting
            levels will be printed.
        sort
            Whether key names should be sorted before printing.
        max_str_len
            The maximum length allowed for strings.
        max_bytes_len
            The maximum length allowed for bytes.
        truncate_suffix
            The suffix to use when truncating strings, bytes or iterables.
        human_bytes
            Whether bytes should be shown as readable strings if it contains
            only printable characters.
        skip_predicate
            A callable predicate that returns whether to skip an attribute
            given its name and value.
        seq_bullet
            The bullet string to use for sequences like lists.
        sep
            The separator to use when there is more than one value.
        inline_singular
            If ``True``, removes the newline and indent before items if they
            only have a single value
    """
    # Avoid global look-up of commonly-used callables
    all_ = all
    bytes_ = bytes
    datetime_ = datetime.datetime
    dict_ = dict
    dir_ = dir
    float_ = float
    getattr_ = getattr
    hasattr_ = hasattr
    id_ = id
    int_ = int
    is_ = isinstance
    len_ = len
    range_ = range
    repr_ = repr
    set_ = set
    str_ = str

    if maximum_depth is None:
        maximum_depth = float_('inf')
    elif maximum_depth <= 0:
        return
    else:
        maximum_depth -= 1

    if stream == str_:
        out = io.StringIO()
    else:
        out = stream or DEFAULT_STREAM

    seen = set_()

    def adapt_key(key):
        if is_(key, str_):
            return key
        elif is_(key, int_):
            return str_(key)
        elif is_(key, bytes_):
            try:
                return key.decode('utf-8')
            except UnicodeDecodeError:
                return '<{} byte{}>'.format(len_(key), '' if len_(key) == 1 else 's')
        else:
            return key.__name__

    def handle_kvp(level, kvp):
        # Keys should always be `str`, we can't print objects in the key-side
        kvp = [(adapt_key(k), v) for k, v in kvp]

        # Iterate twice, one to fix the keys and another for `skip_predicate`
        # which expects `str` and we don't want to call `adapt_key` twice.
        kvp = [(k, v) for k, v in kvp if not skip_predicate(k, v)]

        if sort:
            kvp.sort()

        if inline_singular and len_(kvp) == 1:
            out.write(' ')
            out.write(kvp[0][0])
            out.write(':')
            fmt(kvp[0][1], level, ' ')
        else:
            ind = get_indent(level)
            for key, value in kvp:
                out.write('\n')
                out.write(ind)
                out.write(key)
                out.write(':')
                fmt(value, level, ' ')

    if isinstance(indent, str_):
        def get_indent(level):
            return indent * level
    else:
        def get_indent(level):
            if level == 0:
                return ''
            elif level == 1:
                return indent[0]
            else:
                return indent[0] + (indent[1] * (level - 2)) + indent[-1]

    def fmt(obj, level, space=''):
        """
        Pretty formats the given object as a YAML string which is returned.
        (based on TLObject.pretty_format)
        """
        if obj is None:  # seems None is faster than cached a none
            out.write(space)
            out.write('None')

        elif is_(obj, int_):
            out.write(space)
            out.write(str_(obj))

        elif is_(obj, float_):
            out.write(space)
            out.write('{:.2f}'.format(obj))

        elif is_(obj, datetime_):
            out.write(space)
            out.write(obj.strftime('%Y-%m-%d %H:%M:%S'))

        elif is_(obj, str_):
            out.write(space)
            value = repr_(obj[:max_str_len])[:-1]
            out.write(value)
            if len_(obj) > max_str_len:
                out.write(truncate_suffix)

            out.write(value[0])

        elif is_(obj, bytes_):
            out.write(space)
            if human_bytes and all_(0x20 <= c < 0x7f for c in obj):
                value = repr_(obj[:max_bytes_len])[:-1]
                out.write(value)
                if len_(obj) > max_bytes_len:
                    out.write(truncate_suffix)

                out.write(value[1])
            else:
                out.write('<…>' if len_(obj) > max_bytes_len else
                          ' '.join(f'{b:02X}' for b in obj))

        elif is_(obj, range_):
            out.write(space)
            if obj.start:
                out.write(str_(range))
            else:
                out.write('range({})'.format(obj.stop))

        elif id_(obj) in seen:
            out.write(space)
            out.write('<cyclic reference {:x}>'.format(id_(obj)))

        elif is_(obj, dict_):
            seen.add(id_(obj))
            out.write(space)
            out.write('dict')
            if level < maximum_depth:
                handle_kvp(level + 1, obj.items())

        # Iterating over an IO object yields lines or bytes, and while we
        # could consume those we can seek back in, it's probably best to not
        # print entire files.
        elif hasattr_(obj, '__iter__') and not is_(obj, io.IOBase):
            seen.add(id_(obj))
            out.write(space)
            out.write(obj.__class__.__name__)
            # Special case who wants no space before
            if level < maximum_depth:
                level += 1
                try:
                    for attr in obj:
                        out.write('\n')
                        out.write(get_indent(level))
                        out.write(seq_bullet)
                        fmt(attr, level)
                except TypeError:
                    # `weakproxy` and `weakcallableproxy` pretend to
                    # have `__iter__`, but iterating over them fails.
                    #
                    # Checking against `weakref.ProxyTypes` also seems to fail.
                    out.write(space)
                    out.write('<proxy iterable {:x}>'.format(id_(obj)))

                level -= 1
            else:
                out.write(space)
                out.write('[…]')

        else:
            seen.add(id_(obj))
            out.write(space)
            out.write(obj.__class__.__name__)
            if level < maximum_depth:
                out.write(':')
                handle_kvp(level + 1, ((name, getattr_(obj, name)) for name in dir_(obj)))

    for val in values:
        fmt(val, level=start_indent_level)
        out.write(sep)

    if stream == str_:
        return out.getvalue()