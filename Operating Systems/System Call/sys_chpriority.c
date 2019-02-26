#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/sched.h>
#include <linux/syscalls.h>
#include <linux/rcupdate.h>

asmlinkage long sys_chpriority(pid_t pid1, pid_t pid2, long value)
{
	struct task_struct *p1, *p2;
	
	rcu_read_lock();
	read_lock(&tasklist_lock);
	
	p1 = find_task_by_vpid(pid1);
	p2 = find_task_by_vpid(pid2);
	
	p1->static_prio = PRIO_TO_NICE(p1->static_prio);
	p2->static_prio = PRIO_TO_NICE(p2->static_prio);

	printk("Entring sys_chpriority! ;) \n			TASK1		TASK2\n");
	printk("PIDs:		%d		%d\n",pid1,pid2);
	printk("prio:		%d		%d\n",p1->prio,p2->prio);
	printk("normal_prio:	%d		%d\n\n",p1->normal_prio,p2->normal_prio);

	if(value + p1->static_prio > MAX_NICE){
		printk("Error Bound in MAX_NICE, static_prio = %d\n",p1->static_prio);
		read_unlock(&tasklist_lock);
		rcu_read_unlock();
		return -1;
	}

	if(p2->static_prio - value < MIN_NICE){
		printk("Error Bound in MIN_NICE, static_prio = %d\n",p2->static_prio);
		read_unlock(&tasklist_lock);
		rcu_read_unlock();
		return -1;
	}

	printk("Before Changing Priorities! ;) \n			TASK1		TASK2\n");
	printk("PIDs:		%d		%d\n",pid1,pid2);
	printk("prio:		%d		%d\n",p1->prio,p2->prio);
	printk("normal_prio:	%d		%d\n\n",p1->normal_prio,p2->normal_prio);
	printk("Cahnging Value = %ld\n" , value);

	set_user_nice(p1, p1->static_prio + value);
	set_user_nice(p2, p2->static_prio - value);
	
	printk("After Changing Priorities! ;) \n			TASK1		TASK2\n");
	printk("PIDs:		%d		%d\n",pid1,pid2);
	printk("prio:		%d		%d\n",p1->prio,p2->prio);
	printk("normal_prio:	%d		%d\n\n",p1->normal_prio,p2->normal_prio);

	read_unlock(&tasklist_lock);
	rcu_read_unlock();
	
	return 0;
}
