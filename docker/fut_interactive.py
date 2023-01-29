#!/usr/bin/env python3

import pprint
import shlex
import sys
import termios
import traceback

from framework.server_handler import ServerHandlerClass

pp = pprint.PrettyPrinter(indent=2)


class InteractiveFUTClass:
    def __init__(self):
        self.server = ServerHandlerClass()
        self.dut, self.ref, self.ref2, self.client = None, None, None, None
        try:
            self.dut = self.server.get_test_handler(self.server.get_pod_api('dut'))
        except Exception as e:
            print(f'Could not load DUT\n{e}')
            pass
        try:
            self.ref = self.server.get_test_handler(self.server.get_pod_api('ref'))
        except Exception as e:
            print(f'Could not load REF\n{e}')
            pass
        try:
            self.ref2 = self.server.get_test_handler(self.server.get_pod_api('ref2'))
        except Exception as e:
            print(f'Could not load REF2\n{e}')
            pass
        try:
            self.client = self.server.get_test_handler(self.server.get_pod_api('client'))
        except Exception as e:
            print(f'Could not load CLIENT\n{e}')
            pass

    def _recursive_attr_acquire(self, attr, attr_args):
        if attr_args:
            sub_attr = attr_args.pop(0)
            if hasattr(attr, sub_attr):
                return self._recursive_attr_acquire(getattr(attr, sub_attr), attr_args)
            else:
                return attr, [sub_attr] + attr_args
        return attr, attr_args

    def get_attr(self, handler_name, handler_args=None):
        main_attr = self.__getattribute__(handler_name)
        return self._recursive_attr_acquire(main_attr, handler_args)


interactiveFUT = InteractiveFUTClass()

print('To get help, enter `help`.')

while True:
    try:
        cmd, *args = shlex.split(input('> '))
    except Exception:
        continue

    try:
        if cmd == 'exit':
            break
        elif cmd == 'help':
            print('FUT help message')
        else:
            if not hasattr(interactiveFUT, cmd):
                whole_cmd = f'{cmd} {" ".join(args)}'
                try:
                    eval(whole_cmd)
                except SyntaxError:
                    exec(whole_cmd)
                except Exception:
                    raise
            else:
                attribute, rest_args = interactiveFUT.get_attr(cmd, args)
                print(f'ATTRIBUTE: {attribute}\nREST_ARGS: {rest_args}')
                if callable(attribute):
                    args = []
                    kwargs = {}
                    for a in rest_args:
                        try:
                            try:
                                val = eval(a)
                            except SyntaxError:
                                val = exec(a)
                            except Exception as e:
                                raise e
                            if isinstance(val, dict):
                                kwargs.update(val)
                            elif isinstance(val, list):
                                args += [val]
                            elif '=' in a:
                                kw = a.split('=')
                                kwargs.update({kw[0]: eval(kw[1])})
                            else:
                                args.append(val)
                        except Exception:
                            try:
                                args.append(str(a))
                            except Exception as e:
                                print(f'Will skip value {a}\n{e}')
                                continue
                    args = list(filter(lambda x: x, args))
                    print(f'ARGS: {args}\nKWARGS: {kwargs}')
                    # Pass in rest of args as args or kwargs of method
                    attribute(*args, **kwargs)
                else:
                    pp.pprint(attribute)
    except Exception as e:
        print(traceback.format_exc())
        print(f'Issue during command execution\n{cmd} {args} \n{e}')
    finally:
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
