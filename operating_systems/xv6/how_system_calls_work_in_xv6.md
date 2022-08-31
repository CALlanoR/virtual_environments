### usys.S (macro)
Macro is a function that the compiler substitutes the pattern before makes the real compilation. 

```
#define SYSCALL(name) \
  .globl name; \
  name: \
    movl $SYS_ ## name, %eax; \
    int $T_SYSCALL; \
    ret
```

.globl is an assembler directive that tells the assembler that the main symbol will be accessible from outside the current file (that is, it can be referenced from other files). 

Let’s take getpid syscall and see how it will be replaced in this macro.

```
#define SYSCALL(getpid) \
  .globl getpid; \
  getpid: \
    movl $SYS_ getpid, %eax; \
    int $T_SYSCALL; \
    ret
```

getpid will move the SYS_getpid number defined on syscall.h to the %eax register and will call an interrupt (INT for short) with the T_SYSCALL number (is 64 and is defined on traps.h). 

### vector.S (defines a giant and boring vector table)

```
...
vector63:
  pushl $0
  pushl $63
  jmp alltraps
.globl vector64
vector64:
  pushl $0
  pushl $64
  jmp alltraps
.globl vector65
vector65:
  pushl $0
  pushl $65
  jmp alltraps
.globl vector66
vector66:
  pushl $0
  pushl $66
  jmp alltraps
.globl vector67
...

```

Note: pushl: To push the source operand onto the stack. 

The important thing is that INT $64 will do some stuff and then jumps to vector64 instruction, and this one will push 0 and 64 to the stack before finally call alltraps in trapasm.S. 

### trapasm.S (alltraps was called and it will finish building the trapframe.)
As we are using the memory stack to do this, we are building the struct from bottom to top. The idea is fill trapframe.h. pushal will push the general use registers (eax, ecs, ...). And then finally calls trap() passing the start of trapframe as parameter. 

To avoid returning to this code, let’s see now the trapret instruction: it restores all registers saved on trapframe and this is how the program continues after executing a trap.  

### trap.c


### syscall.c
```
static int (*syscalls[])(void) = {
[SYS_fork]    sys_fork,
[SYS_exit]    sys_exit,
[SYS_wait]    sys_wait,
[SYS_pipe]    sys_pipe,
[SYS_read]    sys_read,
[SYS_kill]    sys_kill,
[SYS_exec]    sys_exec,
[SYS_fstat]   sys_fstat,
[SYS_chdir]   sys_chdir,
[SYS_dup]     sys_dup,
[SYS_getpid]  sys_getpid,
[SYS_sbrk]    sys_sbrk,
[SYS_sleep]   sys_sleep,
[SYS_uptime]  sys_uptime,
[SYS_open]    sys_open,
[SYS_write]   sys_write,
[SYS_mknod]   sys_mknod,
[SYS_unlink]  sys_unlink,
[SYS_link]    sys_link,
[SYS_mkdir]   sys_mkdir,
[SYS_close]   sys_close,
[SYS_getyear] sys_getyear,
};
```

array of function pointers that takes void as parameter and returns int. 
And that thing on the left side of each function? That is just the index we want to put the element in the array, that numbers is defined in syscall.h. 

```
void
syscall(void)
{
  int num;
  struct proc *curproc = myproc();

  num = curproc->tf->eax;
  if(num > 0 && num < NELEM(syscalls) && syscalls[num]) {
    curproc->tf->eax = syscalls[num]();
  } else {
    cprintf("%d %s: unknown sys call %d\n",
            curproc->pid, curproc->name, num);
    curproc->tf->eax = -1;
  }
}
```
now into the syscall() function: it takes that eax register value that we placed on usys.S with the corresponding SYS_* number, calls the sys_syscall from array (that’s syscalls[num]()) and put the result value into eax register (that’s curproc->tf->eax = …) 



