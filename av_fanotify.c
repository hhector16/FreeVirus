#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <limits.h>
#include <string.h>
#include <errno.h>
#include <poll.h>
#include <sys/fanotify.h>
#include <sys/socket.h>
#include <sys/un.h>

#define RUTA_SOCKET "/tmp/av.sock"
#define BUF_LEN 8192

#pragma pack(push, 1)
typedef struct {
    pid_t pid;
    pid_t ppid;
    uint64_t event;
    char path[PATH_MAX];
} paquete;
#pragma pack(pop)


int should_analyze(const char *path) {

    if (strstr(path, "/usr/") == path ||
        strstr(path, "/lib/") == path ||
        strstr(path, "/proc/") == path ||
        strstr(path, "/sys/") == path) {
        return 0;
    }

    if (strstr(path, ".sh") || strstr(path, ".py") ||
        strstr(path, ".bin") || strstr(path, ".com") ||
        strstr(path, ".exe") || strstr(path, ".txt")) {
        return 1;
    }

    return 0;
}




pid_t get_ppid_from_pid(pid_t pid) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/stat", pid);

    FILE *f = fopen(path, "r");
    if (!f)
        return -1;

    pid_t ppid;
    fscanf(f, "%*d (%*[^)]) %*c %d", &ppid);
    fclose(f);

    return ppid;
}

int ask_python(const char *path, pid_t pid, pid_t ppid, uint64_t event) {
    int sock;
    struct sockaddr_un addr;
    char response[16] = {0};
    paquete paquete = {0};

    paquete.pid = pid;
    paquete.ppid = ppid;
    paquete.event = event;
    strncpy(paquete.path, path, PATH_MAX-1);
    paquete.path[PATH_MAX - 1] = '\0';

    sock = socket(AF_UNIX, SOCK_STREAM, 0);
    if (sock < 0)
        return 0;

    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, RUTA_SOCKET, sizeof(addr.sun_path) - 1);

    if (connect(sock, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        close(sock);
        return 0;
    }

    write(sock, &paquete, sizeof(paquete));
    read(sock, response, sizeof(response) - 1);

    close(sock);

    return (strncmp(response, "DENY", 4) == 0);
}

void get_path(int fd, char *buf, size_t size) {
    char fdpath[64];
    char tmp[PATH_MAX];
    snprintf(fdpath, sizeof(fdpath), "/proc/self/fd/%d", fd);
    ssize_t r = readlink(fdpath, tmp, sizeof(tmp) - 1);
    if (r > 0) {
        tmp[r] = 0;
        if (!realpath(tmp, buf)) {
            strncpy(buf, tmp, size - 1);
            buf[size - 1] = 0;
        }
    } else {
        strncpy(buf, "unknown", size - 1);
        buf[size - 1] = 0;
    }
}

void handle_exec(int fan_fd) {
    char buffer[BUF_LEN];
    ssize_t len = read(fan_fd, buffer, sizeof(buffer));
    if (len <= 0)
        return;

    struct fanotify_event_metadata *m;

    for (m = (struct fanotify_event_metadata *)buffer;
         FAN_EVENT_OK(m, len);
         m = FAN_EVENT_NEXT(m, len)) {

        if (m->vers != FANOTIFY_METADATA_VERSION)
            continue;

        if (m->mask & FAN_OPEN) {
            close(m->fd);
            continue;
        }

        if (m->mask & FAN_CLOSE_WRITE) {  

            char path[PATH_MAX];
            get_path(m->fd, path, sizeof(path));

            pid_t ppid = get_ppid_from_pid(m->pid);
            uint64_t event = m->mask;

            printf("[WRITE] %s\n", path); 

            if (strstr(path, "/.config/Code/") != NULL ||
                strstr(path, "/.local/share/gnome-shell") != NULL ||
                strstr(path, "/kubelet") != NULL) {

                struct fanotify_response resp = {
                    .fd = m->fd,
                    .response = FAN_ALLOW
                };

                write(fan_fd, &resp, sizeof(resp));
                continue;   
            }

            ask_python(path, m->pid, ppid, event);
        }

        if (m->mask & FAN_OPEN_EXEC_PERM) {

            char path[PATH_MAX];
            get_path(m->fd, path, sizeof(path));
            pid_t ppid = get_ppid_from_pid(m->pid);
            uint64_t event = m->mask;

            if ((strcmp(path, "/usr/bin/git") != 0) && ((strcmp(path, "/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2") != 0)) &&
             ((strcmp(path, "/usr/lib/systemd/systemd-executor") != 0)) && (strcmp(path, "/usr/bin/bash") != 0)) {
                printf("[EXEC] %s\n", path);
            }

            if (strstr(path, "/.config/Code/") != NULL ||
                strstr(path, "/.local/share/gnome-shell") != NULL ||
                strstr(path, "/kubelet") != NULL) {

                struct fanotify_response resp = {
                    .fd = m->fd,
                    .response = FAN_ALLOW
                };

                write(fan_fd, &resp, sizeof(resp));
                continue;   
            }

            int deny = ask_python(path, m->pid, ppid, event);

            if (deny) {
                printf("Blocked file: %s\n", path);
            }

            struct fanotify_response resp = {
                .fd = m->fd,
                .response = deny ? FAN_DENY : FAN_ALLOW
            };

            write(fan_fd, &resp, sizeof(resp));
        }

        close(m->fd);
    }
}

int main() {

    int fan_exec;

    fan_exec = fanotify_init(
        FAN_CLASS_PRE_CONTENT | FAN_CLOEXEC,
        O_RDONLY | O_LARGEFILE
    );

    if (fan_exec < 0) {
        perror("fanotify_init");
        exit(1);
    }

    fanotify_mark(
        fan_exec,
        FAN_MARK_ADD | FAN_MARK_MOUNT,
        FAN_OPEN_EXEC_PERM | FAN_OPEN | FAN_CLOSE_WRITE,   // <-- AÑADIDO CLOSE_WRITE
        AT_FDCWD,
        "/"
    );

    struct pollfd fds[2];

    fds[1].fd = fan_exec;
    fds[1].events = POLLIN;

    printf("Fanotify activado\n");

    while (1) {

        poll(fds, 2, -1);

        if (fds[1].revents & POLLIN)
            handle_exec(fan_exec);
    }
}