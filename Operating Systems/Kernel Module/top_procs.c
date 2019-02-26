#include <linux/module.h>
#include <linux/init.h>
#include <linux/sched.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>

MODULE_LICENSE("Dual BSD/GPL");

struct PROCESSINFO {
    int pid;
    u64 usermodTime;
    u64 kernelmodTime;
    u64 startTime;
    char command[16];
    kuid_t uid;
    unsigned long long usage;
    unsigned long long totalTime;
};

void insertNewProcess(struct PROCESSINFO to_insert);

struct PROCESSINFO info[16];
int infoSize = 0;

static int tops_show(struct seq_file *m, void *v)
{
    int i;
    for (i = 0; i < 16; i++) {
        info[i].usage = 0;
    }
    int processNum = 0;
    
    struct task_struct *process;
    for_each_process(process) {
        unsigned long long timePassFromBoot = ktime_get_ns();
        struct PROCESSINFO tmp;
        tmp.pid = process->pid;
        tmp.uid = process->cred->uid;
        tmp.usermodTime = (process->utime/HZ) * 1000000000; //ns
        tmp.kernelmodTime = (process->stime/HZ) * 1000000000; //ns
        tmp.startTime = process->start_time;  //ns
        strcpy(tmp.command, process->comm);
        if(timePassFromBoot == tmp.startTime)
            tmp.usage = 0;
        else
            tmp.usage = ((tmp.usermodTime+tmp.kernelmodTime)*10000)/(timePassFromBoot-tmp.startTime);
        processNum++;
        tmp.totalTime = timePassFromBoot-tmp.startTime;

        insertNewProcess(tmp);
    }

    seq_printf(m, "TOP 15 PROCESSES IN ORDER OF CPU USAGE:\n");
    seq_printf(m, "   PID       UID        CPU USAGE      COMMAND\n");
    seq_printf(m, "---------------------------------------------------\n");
    for(i=0;i<15;i++){
        if(info[i].totalTime)
            seq_printf(m, "%6d%10d%5llu.%llu     %s\n", info[i].pid, (info[i].uid).val, (100*(info[i].usermodTime+info[i].kernelmodTime))/info[i].totalTime, (100*(info[i].usermodTime+info[i].kernelmodTime))%info[i].totalTime, info[i].command);
        else
            seq_printf(m, "%6d%10d%5d.%d     %s\n", info[i].pid, (info[i].uid).val, 0, 0, info[i].command);
    }
    return 0;
}

static int tops_open(struct inode *inode, struct file *file)
{
    return single_open(file, tops_show, NULL);
}

static const struct file_operations tops_fops = {
    .owner      = THIS_MODULE,
    .open       = tops_open,
    .read       = seq_read,
    .llseek     = seq_lseek,
    .release    = single_release,
};

static int top_procs_init(void) {
    printk(KERN_ALERT "top_procs Module started\n");
    struct proc_dir_entry* path = proc_mkdir("top_procs", NULL);
    if(path)
        proc_create("tops", 0, path, &tops_fops);

    return 0;
}

void insertNewProcess(struct PROCESSINFO new) {
    int i, j, flag = 0;
    if(infoSize == 0) {
        info[0] = new;
        infoSize++;
        return;
    }
    info[15] = new;
    infoSize = infoSize < 15 ? infoSize + 1 : infoSize;
    for(i = 0; i < 16; i++) {
        for(j = i+1; j < 16; j++) {
            if(info[i].usage < info[j].usage) {
                struct PROCESSINFO tmp = info[i];
                info[i] = info[j];
                info[j] = tmp;
            }
        }
    }
}

//when the module is going to be removed
static void top_procs_exit(void) {
    remove_proc_entry("top_procs", NULL);
    printk(KERN_ALERT "Module removed\n");

}

//macros to define functions
module_init(top_procs_init);
module_exit(top_procs_exit);