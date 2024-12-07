"""
add redpajama prefix to all redpajama imports
"""

import os

if __name__ == '__main__':
    for root, dirs, fns in os.walk('.'):
        for fn in fns:
            print(root,  fn)
            if fn == 'convert.py' or not fn.endswith('py'):
                continue

            fn = f'{root}/{fn}'
            lines = []
            with open(fn) as reader:
                for line in reader:
                    prefixs = ['artifacts', 'core', 'dedup', 'utilities']
                    if any(line.startswith(f'import {prefix}') for prefix in prefixs):
                        line = 'import redpajama.' + line.lstrip('import ')
                        print(line)
                    if any(line.startswith(f'from {prefix}') for prefix in prefixs):
                        line = 'from redpajama.' + line.lstrip('from ')
                        print(line)
                    lines.append(line)
            
            with open(fn, 'w') as writer:
                for line in lines:
                    writer.write(line)
