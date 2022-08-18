# System call
When a program in user mode requires access to RAM or a hardware resource, it must ask the kernel to provide access to that particular resource. This is done via a system call. When a program makes a system call, the mode is switched from user mode to kernel mode.

### How add a custom system call

In order to define your own system call in xv6, you need to make changes to 5 files:

```
1. syscall.h
2. syscall.c
3. sysproc.c
4. usys.S
5. user.h
```

### Write a system call
Edit syscall.h, this file already contains 21 system calls. In order to add the custom system call, the following line needs to be added to this file.

```
#define SYS_getyear 22
```

### Add pointer to the system call in syscall.c
This file contains an array of function pointers which uses the above-defined numbers (indexes) as pointers to system calls which are defined in a different location. 

```
[SYS_getyear] sys_getyear,
```

When the system call with number 22 is called by a user program, the function pointer sys_getyear which has the index SYS_getyear or 22 will call the system call function. 

Add the function prototype in here and we define the function implementation in a different file. The function prototype which needs to be added to the syscall.c file is as follows. 

```
extern int sys_getyear(void);
```


### Implement the system call function
Open the sysproc.c file where system call functions are defined.

```
// return the year of which the Unix version 6 was released
int
sys_getyear(void)
{
return 1975;
}
```

### Add the interface for the system call
In order for a user program to call the system call, an interface needs to be added. Therefore, we need to edit the usys.S file where we should add the following line.

```
SYSCALL(getyear)
```

Next, the user.h file needs to be edited.

```
int getyear(void);
```

### Test the system call
Create this program with the name myprogram.c 

```
#include "types.h"
#include "stat.h"
#include "user.h"
 
int main(void)
{
    printf(1, "Unix V6 was released in the year %d\n", getyear());
    exit();
}
```

### Edit the Makefile
add your program myprogram.c

```
UPROGS=\
_cat\
_crash\
_echo\
_factor\
_forktest\
_grep\
_hello\
_init\
_kill\
_ln\
_ls\
_mkdir\
_null\
_rm\
_sh\
_share\
_stressfs\
_usertests\
_wc\
_zombie\
_myprogram\
```

```
EXTRA=\
mkfs.c ulib.c user.h cat.c echo.c forktest.c grep.c kill.c\
ln.c ls.c mkdir.c rm.c stressfs.c usertests.c wc.c zombie.c\
myprogram.c\
printf.c umalloc.c\
README dot-bochsrc *.pl toc.* runoff runoff1 runoff.list\
.gdbinit.tmpl gdbutil\
```

```
make clean
make
make qemu-nox
```
and then type the name of the program. 
